#!/usr/bin/env python3
"""PAL-ZIP v14 frozen: committee/configuration binding."""

def _lp(s: str) -> str:
    return f"{len(s)}:{s}"

def committee_anchor(members, threshold):
    members = tuple(sorted(set(members)))
    if threshold < 1 or threshold > len(members):
        raise ValueError("invalid threshold")
    return "COMMITTEE|" + _lp(str(threshold)) + "|" + _lp(";".join(members))

def contextual_vote_valid(vote, members, threshold, merge_id, prior_head):
    cid = committee_anchor(members, threshold)
    return (
        vote["voter"] in set(members)
        and vote["merge"] == merge_id
        and vote["prior_head"] == prior_head
        and vote["committee"] == cid
        and vote["decision"] in ("approve", "reject")
    )
