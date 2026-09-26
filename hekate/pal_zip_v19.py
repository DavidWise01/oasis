#!/usr/bin/env python3
"""PAL-ZIP v19 frozen: unanimous-survivor recovery authority."""

def evaluate_recovery_votes(recovery_id, votes, old_members, quarantined):
    survivors = set(old_members) - set(quarantined)
    seen = set()
    approvals = set()
    errors = []

    for v in votes:
        voter = v["voter"]

        if voter in seen:
            errors.append(("duplicate-voter", voter))
            continue
        seen.add(voter)

        if v["recovery"] != recovery_id:
            errors.append(("wrong-recovery", voter))
            continue

        if voter not in survivors:
            errors.append(("not-surviving-old-authority", voter))
            continue

        if v["decision"] == "approve":
            approvals.add(voter)
        elif v["decision"] != "reject":
            errors.append(("bad-decision", voter))

    return {
        "accepted": approvals == survivors,
        "approvals": tuple(sorted(approvals)),
        "errors": tuple(errors),
    }
