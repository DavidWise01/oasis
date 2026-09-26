#!/usr/bin/env python3
"""PAL-ZIP v05 frozen cross-bind reference implementation."""

def _lp(s: str) -> str:
    return f"{len(s)}:{s}"

def pair_anchor(content_anchor, route_anchor: str) -> str:
    """Exact canonical pair representation."""
    e_text = f"{content_anchor[0]}:{content_anchor[1]}"
    return "PAIR|" + _lp(e_text) + "|" + _lp(route_anchor)

def pair_matches(content_anchor, route_anchor: str, trusted_pair_anchor: str) -> bool:
    return pair_anchor(content_anchor, route_anchor) == trusted_pair_anchor
