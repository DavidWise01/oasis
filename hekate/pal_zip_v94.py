#!/usr/bin/env python3
"""PAL-ZIP v94 frozen: chained higher-recovery recovery-rank witnesses."""

def _lp(s: str) -> str:
    return f"{len(s)}:{s}"

def chain_entry(previous_chain_head, exact_v93_rank_witness):
    return (
        "HIGHER-RECOVERY-PREFIX-MERGE-RECOVERY-RANK-CHAIN-ENTRY|"
        + _lp(previous_chain_head) + "|"
        + _lp(exact_v93_rank_witness)
    )

def chain_head(previous_chain_head, exact_v93_rank_witness):
    return (
        "HIGHER-RECOVERY-PREFIX-MERGE-RECOVERY-RANK-CHAIN-HEAD|"
        + _lp(previous_chain_head) + "|"
        + _lp(exact_v93_rank_witness)
    )
