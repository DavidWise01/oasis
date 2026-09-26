#!/usr/bin/env python3
"""PAL-ZIP v36 frozen: sequential policy-lineage resolver."""

def resolve_policy_lineage(events, initial_active, registered_children, rotations):
    current = initial_active
    used_parents = set()

    for parent, child in rotations:
        if parent != current:
            return None
        if child not in registered_children:
            return None
        if parent in used_parents:
            return None

        used_parents.add(parent)
        current = child

    return current
