#!/usr/bin/env python3
"""PAL-ZIP v21 frozen: recovery fork protection."""

def _lp(s: str) -> str:
    return f"{len(s)}:{s}"

def append_head(prior_head: str, entry: str) -> str:
    return "CHAIN|" + _lp(prior_head) + "|" + _lp(entry)

def merge2(a: str, b: str) -> str:
    parents = sorted((a, b))
    if parents[0] == parents[1]:
        raise ValueError("MERGE2 requires distinct parents")
    return "MERGE2|" + _lp(parents[0]) + "|" + _lp(parents[1])
