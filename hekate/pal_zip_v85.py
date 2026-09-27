#!/usr/bin/env python3
"""PAL-ZIP v85 frozen: explicit higher-recovery prefix MERGE2."""

def _lp(s: str) -> str:
    return f"{len(s)}:{s}"

def merge2(parent_a, parent_b):
    if parent_a == parent_b:
        raise ValueError("MERGE2 requires distinct higher-recovery prefix heads")

    a, b = sorted((parent_a, parent_b))

    return (
        "HIGHER-RECOVERY-PREFIX-MERGE2|"
        + _lp(a) + "|"
        + _lp(b)
    )

def merged_higher_recovery_prefix_head(parent_a, parent_b):
    return "MERGED-HIGHER-RECOVERY-PREFIX-HEAD|" + _lp(
        merge2(parent_a, parent_b)
    )
