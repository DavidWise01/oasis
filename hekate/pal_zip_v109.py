#!/usr/bin/env python3
"""PAL-ZIP v109 frozen: explicit clean higher-recovery prefix MERGE2."""

MERGE_LABEL = 'CLEAN-HIGHER-RECOVERY-RANK-PREFIX-MERGE2'
MERGED_HEAD_LABEL = 'MERGED-CLEAN-HIGHER-RECOVERY-RANK-PREFIX-HEAD'

def _lp(s: str) -> str:
    return f"{len(s)}:{s}"

def merge2(parent_a, parent_b):
    if parent_a == parent_b:
        raise ValueError("MERGE2 requires two distinct exact v108 clean prefix heads")
    a, b = sorted((parent_a, parent_b))
    return MERGE_LABEL + "|" + _lp(a) + "|" + _lp(b)

def merged_head(parent_a, parent_b):
    return MERGED_HEAD_LABEL + "|" + _lp(merge2(parent_a, parent_b))
