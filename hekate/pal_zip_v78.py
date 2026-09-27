#!/usr/bin/env python3
"""PAL-ZIP v78 frozen: post-recovery-rank prefix-merge-fork clean recovery."""

def eligible_after_quarantine(members, quarantined):
    return tuple(sorted(set(members) - set(quarantined)))

def recovery_possible(members, quarantined, threshold=2):
    return len(eligible_after_quarantine(members, quarantined)) >= threshold

def recovery_epoch(quarantine_head):
    return (
        "RECOVERY-RANK-PREFIX-MERGE-RECOVERY-EPOCH|"
        + f"{len(quarantine_head)}:{quarantine_head}"
    )
