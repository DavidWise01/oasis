#!/usr/bin/env python3
"""PAL-ZIP v35 frozen: exit-policy rotation lineage."""

def _lp(s: str) -> str:
    return f"{len(s)}:{s}"

def policy_rotate(parent_policy: str, child_policy: str) -> str:
    if parent_policy == child_policy:
        raise ValueError("rotation requires distinct parent and child")
    return "POLICY-ROTATE|" + _lp(parent_policy) + "|" + _lp(child_policy)
