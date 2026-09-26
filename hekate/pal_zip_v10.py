#!/usr/bin/env python3
"""PAL-ZIP v10 frozen quorum certificate."""

def _lp(s: str) -> str:
    return f"{len(s)}:{s}"

def certificate(merge_id: str, votes, evaluate_quorum):
    result = evaluate_quorum(merge_id, votes)
    if not result["accepted"]:
        raise ValueError("cannot certify an unaccepted quorum")

    rows = []
    seen = set()

    for v in votes:
        voter = v["voter"]
        if voter in seen:
            continue
        if v["merge"] != merge_id:
            continue
        if v["decision"] not in ("approve", "reject"):
            continue
        seen.add(voter)
        rows.append(f'{voter}:{v["decision"]}')

    rows.sort()
    return "QCERT|" + _lp(merge_id) + "|" + _lp(";".join(rows))
