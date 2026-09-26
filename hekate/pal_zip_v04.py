#!/usr/bin/env python3
"""PAL-ZIP v04 frozen route/provenance anchor."""

FIELDS = ("id","src","dst","actor","authority","parent","time")

def _lp(s: str) -> str:
    return f"{len(s)}:{s}"

def route_anchor(route) -> str:
    """Reversible canonical serialization for the exact route record."""
    parts = [f"N{len(route)}"]
    for edge in route:
        parts.append("|".join(_lp(str(edge[k])) for k in FIELDS))
    return "\n".join(parts)

def route_changed(current_route, trusted_anchor: str) -> bool:
    return route_anchor(current_route) != trusted_anchor
