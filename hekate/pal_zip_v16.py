#!/usr/bin/env python3
"""PAL-ZIP v16 frozen: context-scoped equivocation quarantine."""

def equivocation_set(votes):
    seen = {}
    bad = set()
    for v in votes:
        if v["decision"] != "approve":
            continue
        key = (v["voter"], v["prior_head"], v["committee"])
        merge = v["merge"]
        if key in seen and seen[key] != merge:
            bad.add(v["voter"])
        else:
            seen[key] = merge
    return frozenset(sorted(bad))

def effective_approvals(votes, merge_id, eligible_members, prior_head, committee_id):
    quarantined = equivocation_set(votes)
    return frozenset(
        v["voter"]
        for v in votes
        if (
            v["decision"] == "approve"
            and v["merge"] == merge_id
            and v["prior_head"] == prior_head
            and v["committee"] == committee_id
            and v["voter"] in set(eligible_members)
            and v["voter"] not in quarantined
        )
    )
