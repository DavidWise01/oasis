#!/usr/bin/env python3
"""PAL-ZIP v89 frozen: append-only higher-recovery prefix-merge quarantine provenance."""

def _lp(s: str) -> str:
    return f"{len(s)}:{s}"

def quarantine_event(parent, auth_epoch, quarantined, evidence_refs):
    q = tuple(sorted(quarantined))
    refs = tuple(sorted(evidence_refs))

    return (
        "HIGHER-RECOVERY-PREFIX-MERGE-QUARANTINE|"
        + _lp(parent) + "|"
        + _lp(auth_epoch) + "|"
        + _lp(";".join(q)) + "|"
        + _lp(";".join(refs))
    )
