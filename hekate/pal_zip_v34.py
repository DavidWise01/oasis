#!/usr/bin/env python3
"""PAL-ZIP v34 frozen: unique active exit policy."""

def active_policy_id(entries, candidate_policies):
    halt_index = None

    for i, entry in enumerate(entries):
        if entry.startswith("SAFE-HALT|"):
            halt_index = i
            break

    if halt_index is None:
        raise ValueError("no SAFE-HALT in history")

    active = []

    for policy_id in candidate_policies:
        marker = f"POLICY-ACTIVE|{len(policy_id)}:{policy_id}"

        if any(i < halt_index and entry == marker for i, entry in enumerate(entries)):
            active.append(policy_id)

    active = tuple(sorted(set(active)))

    return active[0] if len(active) == 1 else None
