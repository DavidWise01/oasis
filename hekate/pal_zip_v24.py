#!/usr/bin/env python3
"""PAL-ZIP v24 frozen: activation after authority-vacuum recovery."""

def _lp(s: str) -> str:
    return f"{len(s)}:{s}"

def vacuum_activation(vacuum_root, recover_id, vrcert, successor_committee_id):
    prefix = "VRCERT|" + _lp(recover_id) + "|"
    if not vrcert.startswith(prefix):
        raise ValueError("VRCERT not bound to exact VACUUM-RECOVER")
    return (
        "VACUUM-ACTIVATE|"
        + _lp(vacuum_root) + "|"
        + _lp(recover_id) + "|"
        + _lp(vrcert) + "|"
        + _lp(successor_committee_id)
    )
