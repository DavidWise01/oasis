#!/usr/bin/env python3
"""PAL-ZIP v106 frozen: chained clean higher-recovery recovery-rank witnesses."""

CHAIN_ROOT = "CLEAN-HIGHER-RECOVERY-RANK-PREFIX-RECOVERY-RANK-CHAIN:ROOT"
CHAIN_ENTRY_LABEL = "CLEAN-HIGHER-RECOVERY-RANK-PREFIX-RECOVERY-RANK-CHAIN-ENTRY"
CHAIN_HEAD_LABEL = "CLEAN-HIGHER-RECOVERY-RANK-PREFIX-RECOVERY-RANK-CHAIN-HEAD"

def _lp(s: str) -> str:
    return f"{len(s)}:{s}"

def chain_entry(previous_chain_head, exact_v105_witness):
    return (
        CHAIN_ENTRY_LABEL + "|"
        + _lp(previous_chain_head) + "|"
        + _lp(exact_v105_witness)
    )

def chain_head(previous_chain_head, exact_v105_witness):
    return (
        CHAIN_HEAD_LABEL + "|"
        + _lp(previous_chain_head) + "|"
        + _lp(exact_v105_witness)
    )
