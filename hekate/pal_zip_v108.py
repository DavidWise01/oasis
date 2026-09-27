#!/usr/bin/env python3
"""PAL-ZIP v108 frozen: clean higher-recovery prefix fork convergence protection."""

PREFIX_HEAD_LABEL = 'CLEAN-HIGHER-RECOVERY-RANK-PREFIX-RECOVERY-RANK-PREFIX-HEAD'

def _lp(s: str) -> str:
    return f"{len(s)}:{s}"

def prefix_head(depth, previous_prefix_head, exact_future_entry):
    if depth < 1:
        raise ValueError("depth must be >= 1")

    return (
        PREFIX_HEAD_LABEL + "|"
        + _lp(str(depth)) + "|"
        + _lp(previous_prefix_head) + "|"
        + _lp(exact_future_entry)
    )

def preserves_divergence(depth, prefix_a, prefix_b, common_future_entry):
    if prefix_a == prefix_b:
        raise ValueError("inputs are not divergent")

    next_a = prefix_head(depth, prefix_a, common_future_entry)
    next_b = prefix_head(depth, prefix_b, common_future_entry)
    return next_a != next_b
