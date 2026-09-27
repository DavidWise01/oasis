#!/usr/bin/env python3
"""PAL-ZIP v93 frozen: higher-recovery recovery-rank witness."""

def _lp(s: str) -> str:
    return f"{len(s)}:{s}"

def rank_witness(
    prior_head,
    eligible_before,
    rank_before,
    quarantined_set,
    evidence_blob,
    quarantine_event,
    eligible_after,
    rank_after,
    status,
    post_head,
):
    return (
        "HIGHER-RECOVERY-PREFIX-MERGE-RECOVERY-RANK-WITNESS|"
        + _lp(prior_head) + "|"
        + _lp(";".join(sorted(eligible_before))) + "|"
        + _lp(str(rank_before)) + "|"
        + _lp(";".join(sorted(quarantined_set))) + "|"
        + _lp(evidence_blob) + "|"
        + _lp(quarantine_event) + "|"
        + _lp(";".join(sorted(eligible_after))) + "|"
        + _lp(str(rank_after)) + "|"
        + _lp(status) + "|"
        + _lp(post_head)
    )
