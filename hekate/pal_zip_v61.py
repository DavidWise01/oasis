#!/usr/bin/env python3
"""PAL-ZIP v61 frozen: explicit merge-rank prefix MERGE2."""

def _lp(s: str) -> str:
    return f"{len(s)}:{s}"

def merge2(parent_a, parent_b):
    if parent_a == parent_b:
        raise ValueError("MERGE2 requires distinct prefix heads")

    a, b = sorted((parent_a, parent_b))

    return (
        "MERGE-RANK-PREFIX-MERGE2|"
        + _lp(a) + "|"
        + _lp(b)
    )

def merged_prefix_head(parent_a, parent_b):
    return "MERGED-MERGE-RANK-PREFIX-HEAD|" + _lp(merge2(parent_a, parent_b))
