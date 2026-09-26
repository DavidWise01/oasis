#!/usr/bin/env python3
"""PAL-ZIP v49 frozen: prefix-aware explicit MERGE2."""

def _lp(s: str) -> str:
    return f"{len(s)}:{s}"

def merge2(parent_a, parent_b):
    if parent_a == parent_b:
        raise ValueError("MERGE2 requires distinct parent heads")

    a, b = sorted((parent_a, parent_b))

    return (
        "PREFIX-MERGE2|"
        + _lp(a) + "|"
        + _lp(b)
    )

def merge_head(parent_a, parent_b):
    merged = merge2(parent_a, parent_b)
    return "MERGED-PREFIX-HEAD|" + _lp(merged)
