#!/usr/bin/env python3
"""PAL-ZIP v03 frozen trusted-anchor reference implementation."""

DIGIT = {"A": 1, "C": 2, "G": 3, "T": 4}

def split_rails(s: str):
    return s[::2], s[1::2]

def rail_palindrome_check(v: str, sh: str, n: int) -> bool:
    if n % 2 == 0:
        return v == sh[::-1]
    return v == v[::-1] and sh == sh[::-1]

def exact_anchor(s: str):
    """
    Injective for finite strings over A/C/G/T.
    Returns (length, base-5 integer), using digits 1..4.
    """
    acc = 0
    for ch in s:
        acc = acc * 5 + DIGIT[ch]
    return (len(s), acc)

def changed_from_baseline(current: str, baseline_anchor) -> bool:
    return exact_anchor(current) != baseline_anchor

def certify_state(current: str, baseline_anchor):
    v, sh = split_rails(current)
    return {
        "palindrome": rail_palindrome_check(v, sh, len(current)),
        "unchanged": exact_anchor(current) == baseline_anchor,
    }
