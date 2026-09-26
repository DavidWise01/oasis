#!/usr/bin/env python3
"""PAL-ZIP v18 frozen: successor committee recovery geometry."""

def _lp(s: str) -> str:
    return f"{len(s)}:{s}"

def committee_anchor(members, threshold):
    members = tuple(sorted(set(members)))
    if threshold < 1 or threshold > len(members):
        raise ValueError("invalid threshold")
    return "COMMITTEE|" + _lp(str(threshold)) + "|" + _lp(";".join(members))

def recovery_event(prior_head, quarantine_id, old_committee_id,
                   quarantined, new_members, new_threshold):
    quarantined = tuple(sorted(set(quarantined)))
    new_members = tuple(sorted(set(new_members)))

    if set(quarantined) & set(new_members):
        raise ValueError("quarantined identity cannot enter successor committee")

    new_cid = committee_anchor(new_members, new_threshold)

    return (
        "RECOVER|"
        + _lp(prior_head) + "|"
        + _lp(quarantine_id) + "|"
        + _lp(old_committee_id) + "|"
        + _lp(";".join(quarantined)) + "|"
        + _lp(new_cid)
    )
