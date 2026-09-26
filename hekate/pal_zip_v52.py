#!/usr/bin/env python3
"""PAL-ZIP v52 frozen: conflicting MERGE2 authorization / merge equivocation."""

def merge_equivocators(votes):
    seen = {}
    bad = set()

    for vote in votes:
        if vote["decision"] != "approve":
            continue

        key = (vote["voter"], vote["parent"], vote["epoch"])
        intent = (vote["peer"], vote["merge_id"])

        if key in seen and seen[key] != intent:
            bad.add(vote["voter"])
        else:
            seen[key] = intent

    return frozenset(sorted(bad))
