#!/usr/bin/env python3
"""PAL-ZIP v66 frozen: post-prefix-merge-fork clean recovery."""

def eligible_after_quarantine(members, quarantined):
    return tuple(sorted(set(members) - set(quarantined)))

def recovery_possible(members, quarantined, threshold):
    return len(eligible_after_quarantine(members, quarantined)) >= threshold

def recovery_epoch(quarantine_head):
    return f"PREFIX-MERGE-RECOVERY-EPOCH|{len(quarantine_head)}:{quarantine_head}"
