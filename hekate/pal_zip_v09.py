#!/usr/bin/env python3
"""PAL-ZIP v09 frozen: 3-of-4 merge authority."""

ELIGIBLE = ("G0", "G1", "G2", "G3")
THRESHOLD = 3

def evaluate_quorum(merge_id: str, votes):
    seen = set()
    approvals = set()
    errors = []

    for v in votes:
        voter = v["voter"]

        if voter not in ELIGIBLE:
            errors.append(("unauthorized-voter", voter))
            continue

        if voter in seen:
            errors.append(("duplicate-voter", voter))
            continue
        seen.add(voter)

        if v["merge"] != merge_id:
            errors.append(("wrong-merge", voter))
            continue

        if v["decision"] == "approve":
            approvals.add(voter)
        elif v["decision"] != "reject":
            errors.append(("bad-decision", voter))

    accepted = (
        not any(kind == "duplicate-voter" for kind, *_ in errors)
        and len(approvals) >= THRESHOLD
    )

    return {
        "accepted": accepted,
        "approvals": tuple(sorted(approvals)),
        "errors": tuple(errors),
    }
