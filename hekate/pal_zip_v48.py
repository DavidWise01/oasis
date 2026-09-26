#!/usr/bin/env python3
"""PAL-ZIP v48 frozen: divergent prefixes cannot silently converge."""

def _lp(s: str) -> str:
    return f"{len(s)}:{s}"

def prefix_head(depth, previous_prefix_head, witness):
    if depth < 1:
        raise ValueError("depth must be >= 1")

    return (
        "PREFIX-HEAD|"
        + _lp(str(depth)) + "|"
        + _lp(previous_prefix_head) + "|"
        + _lp(witness)
    )

def preserves_divergence(depth, head_a, head_b, common_witness):
    if head_a == head_b:
        raise ValueError("inputs are not divergent")

    next_a = prefix_head(depth, head_a, common_witness)
    next_b = prefix_head(depth, head_b, common_witness)

    return next_a != next_b
