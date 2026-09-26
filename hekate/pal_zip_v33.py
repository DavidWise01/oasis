#!/usr/bin/env python3
"""PAL-ZIP v33 frozen: exit-policy ancestry."""

def policy_register(policy_id: str) -> str:
    return f"POLICY-REGISTER|{len(policy_id)}:{policy_id}"

def registered_before_halt(entries, policy_id):
    target = policy_register(policy_id)

    halt_index = None
    for i, entry in enumerate(entries):
        if entry.startswith("SAFE-HALT|"):
            halt_index = i
            break

    if halt_index is None:
        raise ValueError("no SAFE-HALT in history")

    return any(
        i < halt_index and entry == target
        for i, entry in enumerate(entries)
    )
