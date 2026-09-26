#!/usr/bin/env python3
"""PAL-ZIP v07 frozen fork detection."""

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

def common_prefix_length(a_pairs, b_pairs) -> int:
    a = chain_heads(a_pairs)
    b = chain_heads(b_pairs)
    n = min(len(a), len(b))
    i = 0
    while i < n and a[i] == b[i]:
        i += 1
    return i

def fork_index(a_pairs, b_pairs):
    lcp = common_prefix_length(a_pairs, b_pairs)
    if lcp == len(a_pairs) == len(b_pairs):
        return None
    return lcp
