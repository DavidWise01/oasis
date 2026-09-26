#!/usr/bin/env python3
"""PAL-ZIP v43 frozen: recursive quarantine termination."""

def quarantine_step(eligible, quarantined_now, threshold):
    eligible = tuple(sorted(set(eligible)))
    raw_q = tuple(quarantined_now)

    if len(raw_q) != len(set(raw_q)):
        raise ValueError("duplicate identity in quarantine request")

    q = tuple(sorted(set(raw_q)))

    if not q:
        raise ValueError("quarantine must remove at least one identity")

    if not set(q).issubset(set(eligible)):
        raise ValueError("cannot quarantine identity outside current eligible set")

    remaining = tuple(sorted(set(eligible) - set(q)))

    return {
        "before": eligible,
        "quarantined_now": q,
        "after": remaining,
        "decreased": len(remaining) < len(eligible),
        "recovery_possible": len(remaining) >= threshold,
        "safe_halt": len(remaining) < threshold,
    }
