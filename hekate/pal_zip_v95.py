#!/usr/bin/env python3
"""PAL-ZIP v95 frozen: higher-recovery rank-chain prefix commitment."""

def _lp(s: str) -> str:
    return f"{len(s)}:{s}"

def prefix_head(depth, previous_prefix_head, exact_v94_chain_entry):
    if depth < 1:
        raise ValueError("depth must be >= 1")

    return (
        "HIGHER-RECOVERY-PREFIX-MERGE-RECOVERY-RANK-PREFIX-HEAD|"
        + _lp(str(depth)) + "|"
        + _lp(previous_prefix_head) + "|"
        + _lp(exact_v94_chain_entry)
    )
