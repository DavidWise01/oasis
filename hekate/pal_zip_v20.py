#!/usr/bin/env python3
"""PAL-ZIP v20 frozen: successor activation boundary."""

def _lp(s: str) -> str:
    return f"{len(s)}:{s}"

def activation_event(prior_head, recovery_id, recovery_cert, new_committee_id):
    if recovery_id not in recovery_cert:
        raise ValueError("recovery cert not bound to recovery object")
    return (
        "ACTIVATE|"
        + _lp(prior_head) + "|"
        + _lp(recovery_id) + "|"
        + _lp(recovery_cert) + "|"
        + _lp(new_committee_id)
    )

def append_head(prior_head, event):
    return "CHAIN|" + _lp(prior_head) + "|" + _lp(event)
