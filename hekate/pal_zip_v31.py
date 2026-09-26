#!/usr/bin/env python3
"""PAL-ZIP v31 frozen: explicit safe-halt exit authorization policy."""

def _lp(s: str) -> str:
    return f"{len(s)}:{s}"

def policy_anchor(members, threshold):
    members = tuple(sorted(set(members)))
    if threshold < 1 or threshold > len(members):
        raise ValueError("invalid threshold")
    return "EXIT-POLICY|" + _lp(str(threshold)) + "|" + _lp(";".join(members))
