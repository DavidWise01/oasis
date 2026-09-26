#!/usr/bin/env python3
"""PAL-ZIP v37 frozen: policy-rotation authorization."""

def evaluate_rotation(pre_head, parent_policy, child_policy,
                      parent_members, parent_threshold, votes):
    eligible = set(parent_members)
    seen = set()
    approvals = set()
    errors = []

    for vote in votes:
        voter = vote["voter"]

        if voter not in eligible:
            errors.append(("outsider", voter))
            continue
        if voter in seen:
            errors.append(("duplicate", voter))
            continue
        seen.add(voter)

        if vote["pre_head"] != pre_head:
            errors.append(("wrong-head", voter))
            continue
        if vote["parent"] != parent_policy:
            errors.append(("wrong-parent", voter))
            continue
        if vote["child"] != child_policy:
            errors.append(("wrong-child", voter))
            continue

        if vote["decision"] == "approve":
            approvals.add(voter)
        elif vote["decision"] != "reject":
            errors.append(("bad-decision", voter))

    return {
        "accepted": len(approvals) >= parent_threshold,
        "approvals": tuple(sorted(approvals)),
        "errors": tuple(errors),
    }
