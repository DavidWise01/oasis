#!/usr/bin/env python3
"""PAL-ZIP v29 frozen: multiple pre-anchored safe-halt exit forks."""

def detect_exit_conflicts(proposals):
    by_head = {}

    for p in proposals:
        by_head.setdefault(p["halt_head"], []).append(p)

    conflicts = []

    for head, rows in by_head.items():
        intents = {}

        for p in rows:
            intent = (p["action"], p["target"])
            intents.setdefault(intent, set()).add(p["source"])

        if len(intents) > 1:
            conflicts.append((head, intents))

    return conflicts
