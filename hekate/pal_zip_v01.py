#!/usr/bin/env python3
"""PAL-ZIP v01 frozen reference implementation."""
ALPHABET = "ACGT"

def split_rails(s):
    return s[::2], s[1::2]

def rail_palindrome_check(v, sh, n):
    if n % 2 == 0:
        return v == sh[::-1]
    return v == v[::-1] and sh == sh[::-1]

def _idx(rail, k):
    return 2*k if rail == "V" else 2*k+1

def localize_delta_pair(v, sh, n):
    pairs = set()
    if n % 2 == 0:
        m = len(v)
        for k, a in enumerate(v):
            kk = m - 1 - k
            if a != sh[kk]:
                pairs.add(tuple(sorted((_idx("V",k), _idx("S",kk)))))
    else:
        for name, rail in (("V",v),("S",sh)):
            m = len(rail)
            for k in range(m):
                kk = m - 1 - k
                if k >= kk:
                    continue
                if rail[k] != rail[kk]:
                    pairs.add(tuple(sorted((_idx(name,k), _idx(name,kk)))))
    return sorted(pairs)
