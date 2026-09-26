#!/usr/bin/env python3
"""PAL-ZIP v58 frozen: chained merge-authority rank witnesses."""

def _lp(s: str) -> str:
    return f"{len(s)}:{s}"

def chain_entry(previous_chain_head, witness_text):
    return (
        "MERGE-RANK-CHAIN-ENTRY|"
        + _lp(previous_chain_head) + "|"
        + _lp(witness_text)
    )

def chain_head(previous_chain_head, witness_text):
    return (
        "MERGE-RANK-CHAIN-HEAD|"
        + _lp(previous_chain_head) + "|"
        + _lp(witness_text)
    )

def state_continuity(previous, current):
    return (
        previous["status"] == "ACTIVE"
        and current["prior_head"] == previous["post_head"]
        and current["eligible_before"] == previous["eligible_after"]
        and current["rank_before"] == previous["rank_after"]
    )
