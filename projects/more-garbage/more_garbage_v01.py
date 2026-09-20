#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import unicodedata
import zlib
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

# v01: primitive-scoped scanner.
# The stream advances +1 when the current primitive is aligned.
# A NO descends into a bounded local search. Search produces at most
# one recovered output primitive; failure triggers rm/A::xx and advances.

ENCODINGS = ("cp1252", "latin1", "mac_roman")
SUSPICIOUS = set("ÃÂâðŸ€™œžƒ¤¢£¥¦§¨©ª«¬®¯°±²³´µ¶·¸¹º»¼½¾¿√∂")
SEQUENCES = ("Ã", "Â", "â€", "ðŸ", "Ãƒ", "Â©", "‚Ä", "Äô", "√∂", "√ü")

@dataclass(frozen=True)
class Candidate:
    text: str
    path: tuple[str, ...]
    score: int

def badness(text: str) -> int:
    score = 0
    letters = sum(ch.isalpha() for ch in text)
    for ch in text:
        cp = ord(ch)
        cat = unicodedata.category(ch)
        if ch == "\ufffd":
            score += 100
        if ch in SUSPICIOUS:
            score += 4
        if 0x80 <= cp <= 0x9F:
            score += 6
        if cat == "Cc" and ch not in "\t\n\r":
            score += 6
        if cat == "Co":
            score += 20
        if cat in ("Sm", "Sk") and letters >= max(2, len(text) // 3):
            score += 3
    for seq in SEQUENCES:
        score += text.count(seq) * 4
    return score

def primitive_aligned(ch: str) -> bool:
    cp = ord(ch)
    return ch != "\ufffd" and ch not in SUSPICIOUS and not (0x80 <= cp <= 0x9F)

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

def lossless_witness(text: str) -> bool:
    raw = text.encode("utf-8")
    packed = zlib.compress(raw, level=9)
    return zlib.decompress(packed) == raw and zlib.decompress(packed).decode("utf-8") == text

def recover_one_primitive(
    source: str,
    index: int,
    max_window: int = 32,
    max_depth: int = 5,
) -> tuple[Optional[dict], int]:
    """
    Descend from one failed alignment point and search local source windows.
    A valid local repair must:
      1. be exactly reversible to the source window,
      2. strictly reduce mojibake badness,
      3. normalize to exactly one non-combining output primitive,
      4. pass lossless compress/expand witness.

    The longest valid source window wins. That lets one heavily-mangled
    primitive consume its complete local corruption cluster before +1 resumes.
    """
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
            if candidate.score >= source_score:
                continue
            if inverse_path(normalized, candidate.path) != chunk:
                continue
            if not lossless_witness(normalized):
                continue

            choices.append({
                "source": chunk,
                "output": normalized,
                "width": width,
                "path": list(candidate.path),
                "source_badness": source_score,
                "output_badness": candidate.score,
            })

    if not choices:
        return None, checks

    choices.sort(
        key=lambda c: (
            -c["width"],
            c["output_badness"],
            len(c["path"]),
            c["output"],
        )
    )
    return choices[0], checks

def process_stream(source: str, max_window: int = 32, max_depth: int = 5) -> dict:
    i = 0
    output: list[str] = []
    trace: list[dict] = []
    linear_steps = 0
    search_checks = 0
    removed = 0
    repaired = 0

    while i < len(source):
        current = source[i]
        linear_steps += 1

        # Y: aligned primitive. +1 and move on.
        if primitive_aligned(current):
            output.append(current)
            trace.append({
                "index": i,
                "primitive": current,
                "answer": "Y",
                "action": "+1",
            })
            i += 1
            continue

        # U+FFFD is already information loss: rm this primitive and advance.
        if current == "\ufffd":
            removed += 1
            trace.append({
                "index": i,
                "primitive": current,
                "answer": "N",
                "down": [0, 0, 0, -1],
                "action": "rm/A::xx",
                "deleted": True,
                "advanced": True,
            })
            i += 1
            continue

        # N: go down into local search / recursion cost.
        recovered, checks = recover_one_primitive(source, i, max_window, max_depth)
        search_checks += checks

        if recovered is None:
            removed += 1
            trace.append({
                "index": i,
                "primitive": current,
                "answer": "N",
                "down": [0, 0, 0, -1],
                "action": "rm/A::xx",
                "deleted": True,
                "advanced": True,
            })
            i += 1
            continue

        repaired += 1
        output.append(recovered["output"])
        trace.append({
            "index": i,
            "primitive": current,
            "answer": "N",
            "down": [0, 0, 0, -1],
            "action": "search→verify→sort→verify→compress→expand",
            "recovered": recovered,
        })
        i += recovered["width"]

    result = "".join(output)
    return {
        "status": "DONE",
        "input": source,
        "output": result,
        "linear_steps": linear_steps,
        "search_checks": search_checks,
        "cost": linear_steps + search_checks,
        "repaired_primitives": repaired,
        "removed_primitives": removed,
        "complexity_model": {
            "aligned_scan": "n",
            "failed_alignment_search": "n",
            "worst_case": "n^2",
        },
        "distillable_to": ["AETHER", "TEMPORAL"],
        "distill_route": "UNSPECIFIED",
        "trace": trace,
    }

def main() -> None:
    parser = argparse.ArgumentParser(description="MORE GARBAGE primitive-scoped mojibake recycler v01")
    parser.add_argument("text")
    parser.add_argument("--max-window", type=int, default=32)
    parser.add_argument("--max-depth", type=int, default=5)
    args = parser.parse_args()
    print(json.dumps(
        process_stream(args.text, args.max_window, args.max_depth),
        ensure_ascii=False,
        indent=2,
    ))

if __name__ == "__main__":
    main()
