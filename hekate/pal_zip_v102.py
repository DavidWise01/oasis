#!/usr/bin/env python3
"""PAL-ZIP v102 frozen: post-higher-recovery rank-prefix merge-fork clean recovery."""

RECOVERY_EPOCH_LABEL = 'HIGHER-RECOVERY-RANK-PREFIX-MERGE-RECOVERY-EPOCH'

def _lp(s: str) -> str:
    return f"{len(s)}:{s}"

def eligible_after_quarantine(members, quarantined):
    return tuple(sorted(set(members) - set(quarantined)))

def recovery_possible(members, quarantined, threshold=2):
    return len(eligible_after_quarantine(members, quarantined)) >= threshold

def recovery_epoch(quarantine_head):
    return RECOVERY_EPOCH_LABEL + "|" + _lp(quarantine_head)
