#!/usr/bin/env python3
"""PAL-ZIP v38 frozen: rotation-certificate replay protection."""

def _lp(s: str) -> str:
    return f"{len(s)}:{s}"

def authorized_rotation(pre_head, parent, child, cert):
    prefix = (
        "ROTATION-CERT|"
        + _lp(pre_head) + "|"
        + _lp(parent) + "|"
        + _lp(child) + "|"
    )

    if not cert.startswith(prefix):
        raise ValueError("stale or foreign rotation certificate")

    return (
        "AUTHORIZED-ROTATION|"
        + _lp(pre_head) + "|"
        + _lp(parent) + "|"
        + _lp(child) + "|"
        + _lp(cert)
    )
