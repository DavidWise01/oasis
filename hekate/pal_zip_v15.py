#!/usr/bin/env python3
"""PAL-ZIP v15 frozen: quorum intersection / equivocation detection."""

def equivocations(votes):
    """
    Return voters that approved more than one merge
    under the same prior-head + committee context.
    """
    seen = {}
    out = set()
    for v in votes:
        if v["decision"] != "approve":
            continue
        key = (v["voter"], v["prior_head"], v["committee"])
        merge = v["merge"]
        if key in seen and seen[key] != merge:
            out.add(v["voter"])
        else:
            seen[key] = merge
    return out
