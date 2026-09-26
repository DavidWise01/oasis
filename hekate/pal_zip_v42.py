#!/usr/bin/env python3
"""PAL-ZIP v42 frozen: clean-recovery fork protection."""

def clean_recovery_equivocators(votes):
    seen = {}
    bad = set()

    for vote in votes:
        if vote["decision"] != "approve":
            continue

        key = (vote["voter"], vote["head"], vote["parent"])
        child = vote["child"]

        if key in seen and seen[key] != child:
            bad.add(vote["voter"])
        else:
            seen[key] = child

    return frozenset(sorted(bad))
