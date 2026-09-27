#!/usr/bin/env python3
"""PAL-ZIP v86 frozen: higher-recovery prefix MERGE2 authorization."""

def _lp(s: str) -> str:
    return f"{len(s)}:{s}"

def merge2(parent_a, parent_b):
    if parent_a == parent_b:
        raise ValueError("MERGE2 requires distinct higher-recovery prefix heads")

    a, b = sorted((parent_a, parent_b))
    return "HIGHER-RECOVERY-PREFIX-MERGE2|" + _lp(a) + "|" + _lp(b)

def cert_binds(cert, parent, peer, merge_id, auth_epoch, threshold=2):
    prefix = (
        "HIGHER-RECOVERY-PREFIX-MERGE-PARENT-CERT|"
        + _lp(parent) + "|"
        + _lp(peer) + "|"
        + _lp(merge_id) + "|"
        + _lp(auth_epoch) + "|"
        + _lp(str(threshold)) + "|"
    )
    return cert.startswith(prefix)
