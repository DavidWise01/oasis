#!/usr/bin/env python3
"""PAL-ZIP v40 frozen: append-only rotation-quarantine provenance."""

def _lp(s: str) -> str:
    return f"{len(s)}:{s}"

def quarantine_event(pre_head, parent, evidence_map):
    voters = tuple(sorted(evidence_map))
    rows = []

    for voter in voters:
        refs = ";".join(sorted(evidence_map[voter]))
        rows.append(_lp(voter) + ":" + _lp(refs))

    return (
        "ROTATION-QUARANTINE|"
        + _lp(pre_head) + "|"
        + _lp(parent) + "|"
        + _lp(";".join(voters)) + "|"
        + _lp(";".join(rows))
    )
