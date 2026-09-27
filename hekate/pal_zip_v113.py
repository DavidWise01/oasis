#!/usr/bin/env python3
"""PAL-ZIP v113 frozen: append-only clean higher-recovery prefix-merge quarantine provenance."""

QUAR_LABEL = 'CLEAN-HIGHER-RECOVERY-PREFIX-MERGE-QUARANTINE'
HISTORY_LABEL = 'CLEAN-HIGHER-RECOVERY-PREFIX-MERGE-HISTORY'

def _lp(s: str) -> str:
    return f"{len(s)}:{s}"

def quarantine_event(parent, auth_epoch, quarantined, evidence_refs):
    return (
        QUAR_LABEL + "|"
        + _lp(parent) + "|"
        + _lp(auth_epoch) + "|"
        + _lp(";".join(sorted(quarantined))) + "|"
        + _lp(";".join(sorted(evidence_refs)))
    )

def append_head(prior_head, event):
    return HISTORY_LABEL + "|" + _lp(prior_head) + "|" + _lp(event)
