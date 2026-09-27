#!/usr/bin/env python3
"""PAL-ZIP v73 frozen: explicit recovery-rank prefix MERGE2."""

def _lp(s: str) -> str:
    return f"{len(s)}:{s}"

def merge2(parent_a, parent_b):
    if parent_a == parent_b:
        raise ValueError("MERGE2 requires distinct recovery-rank prefix heads")

    a, b = sorted((parent_a, parent_b))

    return (
        "RECOVERY-RANK-PREFIX-MERGE2|"
        + _lp(a) + "|"
        + _lp(b)
    )

def merged_recovery_prefix_head(parent_a, parent_b):
    return "MERGED-RECOVERY-RANK-PREFIX-HEAD|" + _lp(merge2(parent_a, parent_b))
