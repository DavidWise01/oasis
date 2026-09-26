#!/usr/bin/env python3
"""PAL-ZIP v46 frozen: chained rank witnesses."""

def verify_chain_link(previous, current):
    if previous["status"] != "ACTIVE":
        return False

    return (
        current["pre_head"] == previous["post_head"]
        and current["eligible_before"] == previous["eligible_after"]
    )

def valid_rank_progress(current):
    if current["status"] == "ACTIVE":
        return current["rank_after"] < current["rank_before"]

    return current["status"] in ("CLOSED", "HALTED")
