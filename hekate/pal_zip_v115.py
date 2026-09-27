#!/usr/bin/env python3
"""PAL-ZIP v115 frozen: clean prefix-merge recovery-fork protection."""

SECOND_QUAR_LABEL = 'CLEAN-HIGHER-RECOVERY-PREFIX-MERGE-SECOND-QUARANTINE'

def _lp(s: str) -> str:
    return f"{len(s)}:{s}"

def clean_equivocators(votes):
    seen = {}
    bad = set()

    for vote in votes:
        if vote["decision"] != "approve":
            continue

        key = (
            vote["voter"],
            vote["parent"],
            vote["epoch"],
        )
        intent = (
            vote["peer"],
            vote["merge_id"],
        )

        if key in seen and seen[key] != intent:
            bad.add(vote["voter"])
        else:
            seen[key] = intent

    return frozenset(sorted(bad))

def second_quarantine_event(first_quarantine_head, recovery_epoch, clean_equivocators_set, auth_refs):
    if not clean_equivocators_set:
        raise ValueError("second quarantine must be non-empty")

    return (
        SECOND_QUAR_LABEL + "|"
        + _lp(first_quarantine_head) + "|"
        + _lp(recovery_epoch) + "|"
        + _lp(";".join(sorted(clean_equivocators_set))) + "|"
        + _lp(";".join(sorted(auth_refs)))
    )
