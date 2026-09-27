#!/usr/bin/env python3
"""PAL-ZIP v104 frozen: recursive clean higher-recovery rank-prefix quarantine termination."""

from itertools import combinations

THRESHOLD = 2

def admissible_quarantines(eligible):
    eligible = tuple(sorted(eligible))
    if len(eligible) < THRESHOLD:
        return tuple()

    quorums = tuple(
        frozenset(c) for c in combinations(eligible, THRESHOLD)
    )

    out = set()
    for qa in quorums:
        for qb in quorums:
            inter = tuple(sorted(qa & qb))
            if inter:
                out.add(inter)

    return tuple(sorted(out))

def next_state(eligible, quarantined):
    eligible = tuple(sorted(eligible))
    quarantined = tuple(sorted(quarantined))

    if not quarantined:
        raise ValueError("quarantine must be non-empty")
    if not set(quarantined).issubset(set(eligible)):
        raise ValueError("quarantine must be subset of eligible authority")
    if quarantined not in admissible_quarantines(eligible):
        raise ValueError("not an exact admissible clean equivocation set")

    after = tuple(sorted(set(eligible) - set(quarantined)))

    if len(after) >= len(eligible):
        raise ValueError("rank did not strictly decrease")

    status = "ACTIVE" if len(after) >= THRESHOLD else "HALTED"
    return after, status
