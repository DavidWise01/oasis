#!/usr/bin/env python3
"""PAL-ZIP v53 frozen: append-only MERGE2 quarantine provenance."""

def _lp(s: str) -> str:
    return f"{len(s)}:{s}"

def merge_quarantine_event(parent, epoch, quarantined, evidence_map):
    voters = tuple(sorted(quarantined))
    rows = []

    for voter in voters:
        refs = ";".join(sorted(evidence_map[voter]))
        rows.append(_lp(voter) + ":" + _lp(refs))

    return (
        "MERGE-QUARANTINE|"
        + _lp(parent) + "|"
        + _lp(epoch) + "|"
        + _lp(";".join(voters)) + "|"
        + _lp(";".join(rows))
    )
