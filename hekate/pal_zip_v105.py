#!/usr/bin/env python3
"""PAL-ZIP v105 frozen: clean higher-recovery rank-prefix recovery-rank witness."""

WITNESS_LABEL = 'CLEAN-HIGHER-RECOVERY-RANK-PREFIX-RECOVERY-RANK-WITNESS'

def _lp(s: str) -> str:
    return f"{len(s)}:{s}"

def rank_witness(
    prior_head,
    eligible_before,
    rank_before,
    quarantined_set,
    exact_clean_equivocation_evidence,
    exact_quarantine_event,
    eligible_after,
    rank_after,
    status,
    post_head,
):
    return (
        WITNESS_LABEL + "|"
        + _lp(prior_head) + "|"
        + _lp(";".join(sorted(eligible_before))) + "|"
        + _lp(str(rank_before)) + "|"
        + _lp(";".join(sorted(quarantined_set))) + "|"
        + _lp(";".join(sorted(exact_clean_equivocation_evidence))) + "|"
        + _lp(exact_quarantine_event) + "|"
        + _lp(";".join(sorted(eligible_after))) + "|"
        + _lp(str(rank_after)) + "|"
        + _lp(status) + "|"
        + _lp(post_head)
    )
