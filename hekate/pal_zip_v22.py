#!/usr/bin/env python3
"""PAL-ZIP v22 frozen: recovery-authority equivocation."""

def recovery_equivocators(votes):
    seen = {}
    bad = set()

    for v in votes:
        if v["decision"] != "approve":
            continue

        key = (v["voter"], v["recovery_root"])
        recovery_id = v["recovery"]

        if key in seen and seen[key] != recovery_id:
            bad.add(v["voter"])
        else:
            seen[key] = recovery_id

    return frozenset(sorted(bad))
