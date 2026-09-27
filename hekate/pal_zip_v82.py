#!/usr/bin/env python3
"""PAL-ZIP v82 frozen: chained higher-recovery rank witnesses."""

def _lp(s: str) -> str:
    return f"{len(s)}:{s}"

def chain_entry(previous_chain_head, witness):
    return (
        "RECOVERY-RANK-PREFIX-MERGE-RECOVERY-RANK-CHAIN-ENTRY|"
        + _lp(previous_chain_head) + "|"
        + _lp(witness)
    )

def chain_head(previous_chain_head, witness):
    return (
        "RECOVERY-RANK-PREFIX-MERGE-RECOVERY-RANK-CHAIN-HEAD|"
        + _lp(previous_chain_head) + "|"
        + _lp(witness)
    )
