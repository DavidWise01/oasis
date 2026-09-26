#!/usr/bin/env python3
"""PAL-ZIP v47 frozen: recursive chain-prefix commitment."""

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

def verify_prefix_link(depth, previous_prefix_head, witness, candidate_head):
    return candidate_head == prefix_head(
        depth,
        previous_prefix_head,
        witness,
    )
