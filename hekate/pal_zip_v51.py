#!/usr/bin/env python3
"""PAL-ZIP v51 frozen: MERGE2 certificate replay protection."""

def _lp(s: str) -> str:
    return f"{len(s)}:{s}"

def cert_binds(cert, parent_head, peer_head, merge_id, epoch_head, threshold=2):
    prefix = (
        "PARENT-MERGE-CERT|"
        + _lp(parent_head) + "|"
        + _lp(peer_head) + "|"
        + _lp(merge_id) + "|"
        + _lp(epoch_head) + "|"
        + _lp(str(threshold)) + "|"
    )
    return cert.startswith(prefix)
