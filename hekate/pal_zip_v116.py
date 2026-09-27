#!/usr/bin/env python3
"""PAL-ZIP v116 frozen: full clean higher-recovery prefix-merge adversarial closure.

This file intentionally captures the global invariants certified by the
companion frozen report.  The exhaustive harness was executed at freeze time.
"""

MEMBERS = ("T0", "T1", "T2")
THRESHOLD = 2

def quorums(eligible):
    from itertools import combinations
    eligible = tuple(sorted(set(eligible)))
    if len(eligible) < THRESHOLD:
        return tuple()
    return tuple(frozenset(c) for c in combinations(eligible, THRESHOLD))

def quarantine_step(eligible, quarantined, q_ab, q_ac):
    eligible = frozenset(eligible)
    quarantined = frozenset(quarantined)
    overlap = frozenset(q_ab & q_ac)

    if not overlap:
        raise ValueError("conflict quarantine must be non-empty")
    if q_ab not in quorums(eligible) or q_ac not in quorums(eligible):
        raise ValueError("invalid quorum for current eligible authority")

    new_eligible = frozenset(set(eligible) - set(overlap))
    new_quarantined = frozenset(set(quarantined) | set(overlap))

    if not len(new_eligible) < len(eligible):
        raise AssertionError("rank must strictly decrease")
    if set(new_eligible) & set(new_quarantined):
        raise AssertionError("quarantined identity reentry")

    status = "ACTIVE" if len(new_eligible) >= THRESHOLD else "HALTED"
    return new_eligible, new_quarantined, status
