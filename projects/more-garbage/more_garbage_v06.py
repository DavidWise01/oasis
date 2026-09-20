#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import unicodedata
from dataclasses import dataclass
from typing import Optional

ENCODINGS = ("cp1252", "cp1252_loose", "latin1", "mac_roman")

@dataclass(frozen=True)
class Candidate:
    text: str
    path: tuple[str, ...]
    score: int

def badness(text: str) -> int:
    suspicious = set("ÃÂâðŸ€™œžƒ¤¢£¥¦§¨©ª«¬®¯°±²³´µ¶·¸¹º»¼½¾¿√∂")
    sequences = ("Ã", "Â", "â€", "ðŸ", "Ãƒ", "Â©", "‚Ä", "Äô", "√∂", "√ü")
    score = 0
    letters = sum(ch.isalpha() for ch in text)
    for ch in text:
        cp = ord(ch)
        cat = unicodedata.category(ch)
        if ch == "\ufffd":
            score += 100
        if ch in suspicious:
            score += 4
        if 0x80 <= cp <= 0x9F:
            score += 6
        if cat == "Cc" and ch not in "\t\n\r":
            score += 6
        if cat == "Co":
            score += 20
        if cat in ("Sm", "Sk") and letters >= max(2, len(text) // 3):
            score += 3
    for seq in sequences:
        score += text.count(seq) * 4
    return score

_CP1252_DECODE = {
    0x80: "\u20ac", 0x82: "\u201a", 0x83: "\u0192", 0x84: "\u201e",
    0x85: "\u2026", 0x86: "\u2020", 0x87: "\u2021", 0x88: "\u02c6",
    0x89: "\u2030", 0x8a: "\u0160", 0x8b: "\u2039", 0x8c: "\u0152",
    0x8e: "\u017d", 0x91: "\u2018", 0x92: "\u2019", 0x93: "\u201c",
    0x94: "\u201d", 0x95: "\u2022", 0x96: "\u2013", 0x97: "\u2014",
    0x98: "\u02dc", 0x99: "\u2122", 0x9a: "\u0161", 0x9b: "\u203a",
    0x9c: "\u0153", 0x9e: "\u017e", 0x9f: "\u0178",
}
_CP1252_ENCODE = {v: k for k, v in _CP1252_DECODE.items()}
_CP1252_UNDEFINED = {0x81, 0x8d, 0x8f, 0x90, 0x9d}

def _encode_cp1252_loose(text: str) -> bytes:
    out = bytearray()
    for ch in text:
        cp = ord(ch)
        if ch in _CP1252_ENCODE:
            out.append(_CP1252_ENCODE[ch])
        elif cp <= 0x7f or 0xa0 <= cp <= 0xff:
            out.append(cp)
        elif cp in _CP1252_UNDEFINED:
            out.append(cp)
        else:
            raise UnicodeEncodeError("cp1252_loose", ch, 0, 1, "not representable")
    return bytes(out)

def _decode_cp1252_loose(data: bytes) -> str:
    chars = []
    for b in data:
        if b in _CP1252_DECODE:
            chars.append(_CP1252_DECODE[b])
        elif b in _CP1252_UNDEFINED:
            chars.append(chr(b))
        else:
            chars.append(chr(b))
    return "".join(chars)

def repair_step(text: str, encoding: str) -> Optional[str]:
    try:
        if encoding == "cp1252_loose":
            return _encode_cp1252_loose(text).decode("utf-8")
        return text.encode(encoding).decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return None

def inverse_step(text: str, encoding: str) -> Optional[str]:
    try:
        raw = text.encode("utf-8")
        if encoding == "cp1252_loose":
            return _decode_cp1252_loose(raw)
        return raw.decode(encoding)
    except (UnicodeEncodeError, UnicodeDecodeError):
        return None

def inverse_path(text: str, path: tuple[str, ...]) -> Optional[str]:
    current = text
    for encoding in reversed(path):
        current = inverse_step(current, encoding)
        if current is None:
            return None
    return current

def reversible_candidates(source: str, max_depth: int) -> list[Candidate]:
    seen = {source}
    frontier = [(source, ())]
    found: list[Candidate] = []

    for _ in range(max_depth):
        nxt = []
        for text, path in frontier:
            for encoding in ENCODINGS:
                candidate = repair_step(text, encoding)
                if candidate is None or candidate in seen:
                    continue
                seen.add(candidate)
                candidate_path = path + (encoding,)
                if inverse_path(candidate, candidate_path) == source:
                    found.append(Candidate(candidate, candidate_path, badness(candidate)))
                nxt.append((candidate, candidate_path))
        frontier = nxt

    return found

def recover_one_primitive(source: str, index: int, max_window: int = 96, max_depth: int = 10):
    choices = []
    checks = 0
    limit = min(len(source) - index, max_window)
    for width in range(1, limit + 1):
        chunk = source[index:index + width]
        source_score = badness(chunk)
        for candidate in reversible_candidates(chunk, max_depth):
            checks += 1
            normalized = unicodedata.normalize("NFC", candidate.text)
            if len(normalized) != 1:
                continue
            if unicodedata.category(normalized).startswith("M"):
                continue
            if inverse_path(normalized, candidate.path) != chunk:
                continue
            structural_contraction = width > 1 and any(ord(ch) > 127 for ch in chunk)
            if not (candidate.score < source_score or structural_contraction):
                continue
            choices.append({
                "source": chunk,
                "output": normalized,
                "width": width,
                "path": list(candidate.path),
                "source_badness": source_score,
                "output_badness": candidate.score,
                "structural_contraction": structural_contraction,
            })
    if not choices:
        return None, checks
    choices.sort(key=lambda c: (-c["width"], c["output_badness"], len(c["path"]), c["output"]))
    return choices[0], checks

def process_stream(source: str, max_window: int = 96, max_depth: int = 10) -> dict:
    i = 0
    output = []
    trace = []
    search_checks = 0
    repaired = 0
    paused = 0
    while i < len(source):
        current = source[i]
        if current == "\ufffd":
            output.append("?")
            trace.append({
                "index": i,
                "primitive": current,
                "status": "PAUSED",
                "reason": "replacement character: original value not derivable",
                "next_index": i + 1,
            })
            paused += 1
            i += 1
            continue
        recovered, checks = recover_one_primitive(source, i, max_window, max_depth)
        search_checks += checks
        if recovered is None:
            output.append(current)
            trace.append({"index": i, "primitive": current, "status": "PASS"})
            i += 1
            continue
        repaired += 1
        output.append(recovered["output"])
        trace.append({"index": i, "primitive": current, "status": "FOUND", "recovered": recovered})
        i += recovered["width"]
    return {
        "status": "DONE" if paused == 0 else "DONE_WITH_PAUSED",
        "input": source,
        "output": "".join(output),
        "search_checks": search_checks,
        "repaired_primitives": repaired,
        "paused_primitives": paused,
        "trace": trace,
    }

VALID_QUARTERS = ("1/4", "2/4", "3/4", "4/4")

def nibble_suture(text: str, quarter: str = "1/4") -> dict:
    if quarter not in VALID_QUARTERS:
        raise ValueError(f"quarter must be one of {VALID_QUARTERS}")
    holes = [i for i, ch in enumerate(text) if ch == "?"]
    if not holes:
        return {"status":"NO_HOLE","input":text,"nibble":"{"+text+"}","quarter":quarter,"output":text,"deleted":0,"fabricated_replacement":False}
    output = text.replace("?", "")
    return {"status":"SUTURED","input":text,"nibble":"{"+text+"}","quarter":quarter,"hole_indices":holes,"output":output,"deleted":len(holes),"join":"left + right","fabricated_replacement":False}

def process_then_suture(source: str, quarter: str = "1/4", max_window: int = 96, max_depth: int = 10) -> dict:
    stage1 = process_stream(source, max_window=max_window, max_depth=max_depth)
    stage2 = nibble_suture(stage1["output"], quarter=quarter)
    return {"status":stage2["status"],"input":source,"stage1":stage1,"stage2":stage2,"output":stage2["output"]}

MAX_NIBBLE_RECURSE = 4
DELETE_RATE_LITERAL = "~5%"

def recover_nibble_token(nibble: str, attempts: list[dict], error_count: int, next_predictive: bool, at_delete_rate: bool) -> dict:
    if not (nibble.startswith("{") and nibble.endswith("}")):
        nibble = "{" + nibble + "}"
    trace = []
    for recurse, attempt in enumerate(attempts[:MAX_NIBBLE_RECURSE], start=1):
        recoverable = bool(attempt.get("recoverable", False))
        token = attempt.get("token")
        trace.append({"recurse":recurse,"recoverable":recoverable,"token":token if recoverable else None})
        if recoverable:
            if token is None:
                raise ValueError("recoverable attempt requires token")
            return {"status":"RECOVERED_TOKEN","nibble":nibble,"token":token,"recurse_used":recurse,"max_recurse":MAX_NIBBLE_RECURSE,"mandel":"BOUND","reincarnated":True,"original_primitive_known":False,"original_primitive":None,"trace":trace}
    if error_count >= 2 and not next_predictive and at_delete_rate:
        return {"status":"DELETE_FULL_NIBBLE","nibble":nibble,"token":"","recurse_used":min(len(attempts),MAX_NIBBLE_RECURSE),"max_recurse":MAX_NIBBLE_RECURSE,"errors":error_count,"next_predictive":False,"delete_rate":DELETE_RATE_LITERAL,"mandel":"CONTINUE_AFTER_DELETE","reincarnated":False,"original_primitive_known":False,"trace":trace}
    return {"status":"REENTER_MANDEL","nibble":nibble,"token":nibble[1:-1],"recurse_used":min(len(attempts),MAX_NIBBLE_RECURSE),"max_recurse":MAX_NIBBLE_RECURSE,"errors":error_count,"next_predictive":next_predictive,"delete_rate":DELETE_RATE_LITERAL,"mandel":"SEARCH","reincarnated":False,"original_primitive_known":False,"trace":trace}

def close_deleted_nibble(left_words: str, right_words: str) -> str:
    return " ".join((left_words.rstrip(), right_words.lstrip())).strip()

HEX32_RE = re.compile(r"^[0-9A-Fa-f]{8}$")
KERNEL_GATE = "|"
KERNEL_BRIDGE = "/_"

def classify_32dword_island(text: str) -> dict:
    if len(text) == 10 and text[0] in ("x", "X") and text[-1] in ("x", "X"):
        core = text[1:-1]
        if HEX32_RE.fullmatch(core):
            return {"status":"MANTISSA_ISLAND","input":text,"core":core.upper(),"hex_digits":8,"bits":32,"left_gate":text[0],"right_gate":text[-1],"output":text}
    if len(text) == 10 and text[0] == KERNEL_GATE and text[-1] == KERNEL_GATE:
        core = text[1:-1]
        if HEX32_RE.fullmatch(core):
            output = KERNEL_BRIDGE + core.upper() + KERNEL_BRIDGE
            return {"status":"KERNEL_BRIDGE","input":text,"core":core.upper(),"hex_digits":8,"bits":32,"left_gate":KERNEL_GATE,"right_gate":KERNEL_GATE,"transmutation":"| -> /_","output":output}
    return {"status":"NOT_32DWORD_ISLAND","input":text,"output":text}

def main() -> None:
    parser = argparse.ArgumentParser(description="MORE GARBAGE mojibake recovery v06")
    parser.add_argument("text")
    parser.add_argument("--max-window", type=int, default=96)
    parser.add_argument("--max-depth", type=int, default=10)
    args = parser.parse_args()
    print(json.dumps(process_stream(args.text, args.max_window, args.max_depth), ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
