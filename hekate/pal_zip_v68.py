#!/usr/bin/env python3
"""PAL-ZIP v68 frozen: recursive prefix-merge quarantine termination."""

def authority_rank(eligible):
    return len(tuple(sorted(set(eligible))))

def valid_quarantine_transition(eligible_before, quarantined, threshold=2):
    before = set(eligible_before)
    q = set(quarantined)

    if not q:
        return False

    if not q.issubset(before):
        return False

    after = before - q
    rb = len(before)
    ra = len(after)

    return {
        "rank_before": rb,
        "rank_after": ra,
        "status": "ACTIVE" if ra >= threshold else "HALTED",
        "strictly_decreases": ra < rb,
    }
