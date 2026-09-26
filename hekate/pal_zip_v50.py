#!/usr/bin/env python3
"""PAL-ZIP v50 frozen: prefix-aware MERGE2 dual-parent authorization."""

def _lp(s: str) -> str:
    return f"{len(s)}:{s}"

def merge2(parent_a, parent_b):
    if parent_a == parent_b:
        raise ValueError("MERGE2 requires distinct parent heads")

    a, b = sorted((parent_a, parent_b))
    return "PREFIX-MERGE2|" + _lp(a) + "|" + _lp(b)

def cert_binds(cert, parent_head, merge_id, threshold):
    prefix = (
        "PARENT-MERGE-CERT|"
        + _lp(parent_head) + "|"
        + _lp(merge_id) + "|"
        + _lp(str(threshold)) + "|"
    )
    return cert.startswith(prefix)

def authorized_merge2(parent_a, parent_b, cert_a, cert_b, threshold=2):
    merge_id = merge2(parent_a, parent_b)

    if not cert_binds(cert_a, parent_a, merge_id, threshold):
        raise ValueError("parent A certificate invalid")

    if not cert_binds(cert_b, parent_b, merge_id, threshold):
        raise ValueError("parent B certificate invalid")

    pairs = sorted(((parent_a, cert_a), (parent_b, cert_b)), key=lambda x: x[0])

    return (
        "AUTHORIZED-PREFIX-MERGE2|"
        + _lp(merge_id) + "|"
        + _lp(pairs[0][0]) + "|"
        + _lp(pairs[0][1]) + "|"
        + _lp(pairs[1][0]) + "|"
        + _lp(pairs[1][1])
    )
