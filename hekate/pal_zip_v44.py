#!/usr/bin/env python3
"""PAL-ZIP v44 frozen: explicit termination rank."""

def authority_rank(eligible):
    return len(tuple(sorted(set(eligible))))

def valid_progress(rank_before, rank_after, status):
    if status == "ACTIVE":
        return rank_after < rank_before
    if status in ("CLOSED", "HALTED"):
        return True
    return False
