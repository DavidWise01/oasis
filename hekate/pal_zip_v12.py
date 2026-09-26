#!/usr/bin/env python3
"""PAL-ZIP v12 frozen: stale/replay quorum protection."""

ELIGIBLE = ("G0", "G1", "G2", "G3")
THRESHOLD = 3

def _lp(s: str) -> str:
    return f"{len(s)}:{s}"

def evaluate_quorum(merge_id: str, prior_head: str, votes):
    seen = set()
    approvals = set()
    errors = []
    for v in votes:
        voter = v["voter"]
        if voter not in ELIGIBLE:
            errors.append(("unauthorized-voter", voter)); continue
        if voter in seen:
            errors.append(("duplicate-voter", voter)); continue
        seen.add(voter)
        if v["merge"] != merge_id:
            errors.append(("wrong-merge", voter)); continue
        if v["prior_head"] != prior_head:
            errors.append(("stale-or-wrong-head", voter)); continue
        if v["decision"] == "approve":
            approvals.add(voter)
        elif v["decision"] != "reject":
            errors.append(("bad-decision", voter))
    return {
        "accepted": (
            not any(kind == "duplicate-voter" for kind, *_ in errors)
            and len(approvals) >= THRESHOLD
        ),
        "approvals": tuple(sorted(approvals)),
        "errors": tuple(errors),
    }

def qcert(merge_id: str, prior_head: str, votes):
    result = evaluate_quorum(merge_id, prior_head, votes)
    if not result["accepted"]:
        raise ValueError("cannot certify an unaccepted quorum")
    rows = []
    seen = set()
    for v in votes:
        if v["voter"] in seen: continue
        if v["voter"] not in ELIGIBLE: continue
        if v["merge"] != merge_id or v["prior_head"] != prior_head: continue
        if v["decision"] not in ("approve", "reject"): continue
        seen.add(v["voter"])
        rows.append(f'{v["voter"]}:{v["decision"]}')
    rows.sort()
    return "QCERT2|" + _lp(merge_id) + "|" + _lp(prior_head) + "|" + _lp(";".join(rows))

def authmerge(merge_id: str, prior_head: str, cert: str):
    prefix = "QCERT2|" + _lp(merge_id) + "|" + _lp(prior_head) + "|"
    if not cert.startswith(prefix):
        raise ValueError("certificate not bound to exact merge + prior head")
    return "AUTHMERGE2|" + _lp(prior_head) + "|" + _lp(merge_id) + "|" + _lp(cert)
