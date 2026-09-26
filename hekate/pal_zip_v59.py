#!/usr/bin/env python3
"""PAL-ZIP v59 frozen: merge-rank chain prefix commitment."""

def _lp(s: str) -> str:
    return f"{len(s)}:{s}"

def prefix_head(depth, previous_prefix_head, exact_chain_entry):
    if depth < 1:
        raise ValueError("depth must be >= 1")

    return (
        "MERGE-RANK-PREFIX-HEAD|"
        + _lp(str(depth)) + "|"
        + _lp(previous_prefix_head) + "|"
        + _lp(exact_chain_entry)
    )

def verify_prefix_link(depth, previous_prefix_head, exact_chain_entry, candidate):
    return candidate == prefix_head(depth, previous_prefix_head, exact_chain_entry)
