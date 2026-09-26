#!/usr/bin/env python3
"""PAL-ZIP v39 frozen: certified policy-rotation fork."""

def rotation_equivocators(votes):
    seen = {}
    bad = set()

    for vote in votes:
        if vote["decision"] != "approve":
            continue

        key = (vote["voter"], vote["pre_head"], vote["parent"])
        child = vote["child"]

        if key in seen and seen[key] != child:
            bad.add(vote["voter"])
        else:
            seen[key] = child

    return frozenset(sorted(bad))
