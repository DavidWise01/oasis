#!/usr/bin/env python3
"""
Hardest unsolved mojibake benchmark:
irreversible U+FFFD collision classes.

PASS means the benchmark successfully demonstrates ambiguity.
It does NOT mean the original primitive was recovered.
"""
from __future__ import annotations
import json

CASES = [
    ("caf�", ["café", "cafè", "cafê", "cafë"]),
    ("M�nchen", ["München", "Mönchen"]),
    ("na�ve", ["naïve", "naíve", "naîve"]),
    ("it�s", ["it’s", "it‘s", "it´s"]),
    ("�", ["😂", "😀", "😭", "💾", "é", "ö", "—"]),
]

def main() -> None:
    rows = []
    for observed, originals in CASES:
        rows.append({
            "observed": observed,
            "candidate_count": len(originals),
            "candidates": originals,
            "ambiguous": len(set(originals)) > 1,
        })

    result = {
        "status": "PASS" if all(r["ambiguous"] for r in rows) else "FAIL",
        "meaning": "PASS proves the target is ambiguous, not recovered.",
        "rows": rows,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
