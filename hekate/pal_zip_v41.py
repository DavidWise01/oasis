#!/usr/bin/env python3
"""PAL-ZIP v41 frozen: clean post-fork rotation recovery."""

def evaluate_clean_recovery(quarantine_head, parent, child,
                            parent_members, parent_threshold,
                            quarantined, votes):
    eligible = set(parent_members) - set(quarantined)
    seen = set()
    approvals = set()
    errors = []

    for vote in votes:
        voter = vote["voter"]

        if voter not in eligible:
            errors.append(("ineligible-or-quarantined", voter))
            continue
        if voter in seen:
            errors.append(("duplicate", voter))
            continue
        seen.add(voter)

        if vote["head"] != quarantine_head:
            errors.append(("stale-head", voter))
            continue
        if vote["parent"] != parent:
            errors.append(("wrong-parent", voter))
            continue
        if vote["child"] != child:
            errors.append(("wrong-child", voter))
            continue

        if vote["decision"] == "approve":
            approvals.add(voter)
        elif vote["decision"] != "reject":
            errors.append(("bad-decision", voter))

    return {
        "accepted": len(approvals) >= parent_threshold,
        "eligible": tuple(sorted(eligible)),
        "approvals": tuple(sorted(approvals)),
        "errors": tuple(errors),
    }
