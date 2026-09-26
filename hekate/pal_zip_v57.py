#!/usr/bin/env python3
"""PAL-ZIP v57 frozen: merge-authority rank witness."""

def verify_rank_decrease(eligible_before, quarantined, eligible_after, threshold=2):
    before = set(eligible_before)
    q = set(quarantined)
    after = set(eligible_after)

    if not q:
        return False

    if not q.issubset(before):
        return False

    if after != before - q:
        return False

    rank_before = len(before)
    rank_after = len(after)

    if not rank_after < rank_before:
        return False

    return {
        "rank_before": rank_before,
        "rank_after": rank_after,
        "status": "ACTIVE" if rank_after >= threshold else "HALTED",
    }
