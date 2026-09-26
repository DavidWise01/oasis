#!/usr/bin/env python3
"""PAL-ZIP v25 frozen: reserve equivocation/capture detection."""

def reserve_equivocators(votes):
    seen = {}
    bad = set()

    for v in votes:
        if v["decision"] != "approve":
            continue

        key = (v["voter"], v["vacuum_root"])
        recover_id = v["recover"]

        if key in seen and seen[key] != recover_id:
            bad.add(v["voter"])
        else:
            seen[key] = recover_id

    return frozenset(sorted(bad))
