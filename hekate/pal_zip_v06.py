#!/usr/bin/env python3
"""PAL-ZIP v06 frozen append-only exact head."""

def _lp(s: str) -> str:
    return f"{len(s)}:{s}"

def chain_heads(pair_anchors, root: str = "ROOT:-i"):
    heads = []
    prev = root
    for idx, pair in enumerate(pair_anchors):
        head = "CHAIN|" + _lp(str(idx)) + "|" + _lp(prev) + "|" + _lp(pair)
        heads.append(head)
        prev = head
    return heads

def exact_head(pair_anchors, root: str = "ROOT:-i") -> str:
    heads = chain_heads(pair_anchors, root)
    return heads[-1] if heads else root

def unchanged(pair_anchors, trusted_external_head: str) -> bool:
    return exact_head(pair_anchors) == trusted_external_head
