#!/usr/bin/env python3
"""PAL-ZIP v11 frozen: authorized merge as permanent history."""

def _lp(s: str) -> str:
    return f"{len(s)}:{s}"

def authmerge(merge_id: str, cert: str) -> str:
    prefix = "QCERT|" + _lp(merge_id) + "|"
    if not cert.startswith(prefix):
        raise ValueError("certificate does not bind this merge")
    return "AUTHMERGE|" + _lp(merge_id) + "|" + _lp(cert)

def chain_head(entries, root: str = "ROOT:-i") -> str:
    prev = root
    for idx, entry in enumerate(entries):
        prev = "CHAIN|" + _lp(str(idx)) + "|" + _lp(prev) + "|" + _lp(entry)
    return prev
