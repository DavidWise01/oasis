#!/usr/bin/env python3
"""PAL-ZIP v26 frozen: append-only reserve-quarantine provenance."""

def _lp(s: str) -> str:
    return f"{len(s)}:{s}"

def reserve_quarantine_event(vacuum_root, reserve_committee_id, evidence_map):
    voters = tuple(sorted(evidence_map))
    rows = []

    for voter in voters:
        refs = ";".join(sorted(evidence_map[voter]))
        rows.append(_lp(voter) + ":" + _lp(refs))

    return (
        "RESERVE-QUARANTINE|"
        + _lp(vacuum_root) + "|"
        + _lp(reserve_committee_id) + "|"
        + _lp(";".join(voters)) + "|"
        + _lp(";".join(rows))
    )
