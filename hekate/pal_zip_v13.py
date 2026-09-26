#!/usr/bin/env python3
"""PAL-ZIP v13 frozen: mixed-epoch vote splicing is rejected."""

def contextual_vote_valid(vote, eligible, merge_id, prior_head):
    return (
        vote["voter"] in eligible
        and vote["merge"] == merge_id
        and vote["prior_head"] == prior_head
        and vote["decision"] in ("approve", "reject")
    )
