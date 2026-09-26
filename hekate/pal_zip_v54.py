#!/usr/bin/env python3
"""PAL-ZIP v54 frozen: post-merge-fork clean recovery."""

def eligible_after_quarantine(members, quarantined):
    return tuple(sorted(set(members) - set(quarantined)))

def recovery_possible(members, quarantined, threshold):
    return len(eligible_after_quarantine(members, quarantined)) >= threshold
