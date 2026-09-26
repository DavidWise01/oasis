#!/usr/bin/env python3
"""PAL-ZIP v08 frozen two-parent merge."""

def _lp(s: str) -> str:
    return f"{len(s)}:{s}"

def merge_anchor(parent_heads) -> str:
    """
    Deterministic order-independent two-parent merge identity.
    Preserves both parent heads; does not choose a winner.
    """
    parents = sorted(parent_heads)
    if len(parents) != 2:
        raise ValueError("merge requires exactly two parents")
    if parents[0] == parents[1]:
        raise ValueError("merge parents must be distinct")
    return "MERGE2|" + _lp(parents[0]) + "|" + _lp(parents[1])
