#!/usr/bin/env python3
"""PAL-ZIP v112 frozen: conflicting clean higher-recovery prefix MERGE2 authorization."""

QUAR_LABEL = 'CLEAN-HIGHER-RECOVERY-PREFIX-MERGE-QUARANTINE'

def _lp(s: str) -> str:
    return f"{len(s)}:{s}"

def equivocators(votes):
    seen = {}
    bad = set()

    for vote in votes:
        if vote["decision"] != "approve":
            continue

        key = (
            vote["voter"],
            vote["parent"],
            vote["auth_epoch"],
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

def quarantine_event(parent, auth_epoch, quarantined, auth_refs):
    return (
        QUAR_LABEL + "|"
        + _lp(parent) + "|"
        + _lp(auth_epoch) + "|"
        + _lp(";".join(sorted(quarantined))) + "|"
        + _lp(";".join(sorted(auth_refs)))
    )
