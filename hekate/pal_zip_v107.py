#!/usr/bin/env python3
"""PAL-ZIP v107 frozen: clean higher-recovery rank-chain prefix commitment."""

PREFIX_ROOT = 'CLEAN-HIGHER-RECOVERY-RANK-PREFIX-RECOVERY-RANK-PREFIX:ROOT'
PREFIX_HEAD_LABEL = 'CLEAN-HIGHER-RECOVERY-RANK-PREFIX-RECOVERY-RANK-PREFIX-HEAD'

def _lp(s: str) -> str:
    return f"{len(s)}:{s}"

def prefix_head(depth, previous_prefix_head, exact_v106_chain_entry):
    if depth < 1:
        raise ValueError("depth must be >= 1")

    return (
        PREFIX_HEAD_LABEL + "|"
        + _lp(str(depth)) + "|"
        + _lp(previous_prefix_head) + "|"
        + _lp(exact_v106_chain_entry)
    )
