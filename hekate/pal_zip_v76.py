#!/usr/bin/env python3
"""PAL-ZIP v76 frozen: conflicting recovery-rank prefix MERGE2 authorization."""

def recovery_prefix_merge_equivocators(votes):
    seen = {}
    bad = set()

    for vote in votes:
        if vote["decision"] != "approve":
            continue

        key = (
            vote["voter"],
            vote["parent"],
            vote["auth_epoch"],
        )
        intent = (
            vote["peer"],
            vote["merge_id"],
        )

        if key in seen and seen[key] != intent:
            bad.add(vote["voter"])
        else:
            seen[key] = intent

    return frozenset(sorted(bad))
