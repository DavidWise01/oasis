#!/usr/bin/env python3
"""PAL-ZIP v27 frozen: safe-halt invariant."""

PRIVILEGED_ACTIONS = ("RECOVER", "ACTIVATE", "MERGE", "VOTE")

def _lp(s: str) -> str:
    return f"{len(s)}:{s}"

def transition(action, current_head, operating_authority, reserve_authority,
               source_anchor=None, source_preanchored=False):
    if action not in PRIVILEGED_ACTIONS:
        raise ValueError("unknown privileged action")

    if operating_authority or reserve_authority:
        return {
            "advanced": False,
            "reason": "not-in-v27-safe-halt-domain",
            "head": current_head,
        }

    if not source_anchor or not source_preanchored:
        return {
            "advanced": False,
            "reason": "safe-halt-no-preanchored-authority",
            "head": current_head,
        }

    event = (
        "SAFE-HALT-EXIT|"
        + _lp(action)
        + "|"
        + _lp(current_head)
        + "|"
        + _lp(source_anchor)
    )

    return {
        "advanced": True,
        "reason": "preanchored-authority",
        "head": "CHAIN|" + _lp(current_head) + "|" + _lp(event),
        "event": event,
    }
