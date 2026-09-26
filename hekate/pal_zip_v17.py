#!/usr/bin/env python3
"""PAL-ZIP v17 frozen: append-only quarantine provenance."""

def _lp(s: str) -> str:
    return f"{len(s)}:{s}"

def quarantine_event(prior_head: str, committee: str, evidence_map) -> str:
    voters = sorted(evidence_map)
    rows = []
    for voter in voters:
        refs = ";".join(sorted(evidence_map[voter]))
        rows.append(_lp(voter) + ":" + _lp(refs))
    return (
        "QUARANTINE|"
        + _lp(prior_head)
        + "|"
        + _lp(committee)
        + "|"
        + _lp(";".join(voters))
        + "|"
        + _lp(";".join(rows))
    )

def append_head(prior_history_head: str, event: str) -> str:
    return "CHAIN|" + _lp(prior_history_head) + "|" + _lp(event)
