#!/usr/bin/env python3
"""PAL-ZIP v45 frozen: rank witness verification."""

def authority_rank(eligible):
    return len(tuple(sorted(set(eligible))))

def verify_rank_values(eligible_before, eligible_after, rank_before, rank_after):
    return (
        authority_rank(eligible_before) == rank_before
        and authority_rank(eligible_after) == rank_after
    )
