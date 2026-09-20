#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import unicodedata
from dataclasses import dataclass
from typing import Optional

ENCODINGS = ("cp1252", "latin1", "mac_roman")

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

def repair_step(text: str, encoding: str) -> Optional[str]:
    try:
        return text.encode(encoding).decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return None

def inverse_step(text: str, encoding: str) -> Optional[str]:
    try:
        return text.encode("utf-8").decode(encoding)
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
        return {
            "status": "NO_HOLE",
            "input": text,
            "nibble": "{" + text + "}",
            "quarter": quarter,
            "output": text,
            "deleted": 0,
            "fabricated_replacement": False,
        }
    output = text.replace("?", "")
    return {
        "status": "SUTURED",
        "input": text,
        "nibble": "{" + text + "}",
        "quarter": quarter,
        "hole_indices": holes,
        "output": output,
        "deleted": len(holes),
        "join": "left + right",
        "fabricated_replacement": False,
    }

def process_then_suture(source: str, quarter: str = "1/4", max_window: int = 96, max_depth: int = 10) -> dict:
    stage1 = process_stream(source, max_window=max_window, max_depth=max_depth)
    stage2 = nibble_suture(stage1["output"], quarter=quarter)
    return {
        "status": stage2["status"],
        "input": source,
        "stage1": stage1,
        "stage2": stage2,
        "output": stage2["output"],
    }

def main() -> None:
    parser = argparse.ArgumentParser(description="MORE GARBAGE mojibake search + nibble surgery v03")
    parser.add_argument("text")
    parser.add_argument("--quarter", choices=VALID_QUARTERS, default="1/4")
    parser.add_argument("--max-window", type=int, default=96)
    parser.add_argument("--max-depth", type=int, default=10)
    args = parser.parse_args()
    print(json.dumps(
        process_then_suture(args.text, args.quarter, args.max_window, args.max_depth),
        ensure_ascii=False,
        indent=2,
    ))

if __name__ == "__main__":
    main()
