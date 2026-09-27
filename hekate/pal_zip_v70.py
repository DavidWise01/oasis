#!/usr/bin/env python3
"""PAL-ZIP v70 frozen: chained prefix-merge recovery rank witnesses."""

def _lp(s: str) -> str:
    return f"{len(s)}:{s}"

def chain_entry(previous_chain_head, witness):
    return (
        "PREFIX-MERGE-RECOVERY-RANK-CHAIN-ENTRY|"
        + _lp(previous_chain_head) + "|"
        + _lp(witness)
    )

def chain_head(previous_chain_head, witness):
    return (
        "PREFIX-MERGE-RECOVERY-RANK-CHAIN-HEAD|"
        + _lp(previous_chain_head) + "|"
        + _lp(witness)
    )

def valid_continuity(previous, current):
    return (
        previous["status"] == "ACTIVE"
        and current["prior_head"] == previous["post_head"]
        and current["eligible_before"] == previous["eligible_after"]
        and current["rank_before"] == previous["rank_after"]
    )
