#!/usr/bin/env python3
"""PAL-ZIP v56 frozen: recursive merge-quarantine termination."""

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

    return {
        "rank_before": len(before),
        "rank_after": len(after),
        "status": "ACTIVE" if len(after) >= threshold else "HALTED",
        "strictly_decreases": len(after) < len(before),
    }
