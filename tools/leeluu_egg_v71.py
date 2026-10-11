"""LEELUU EGG v71: 0(i.u.us) recurrent symbolic VM.

No tests or historical decoding claims. 0 is pinned; snapshots append.
Four logical cores; 120 lanes; five sublanes; three explorers.
"""
from dataclasses import dataclass
import hashlib
import json

ROWS = "ABCDEFGHIJKLMNOP"
ADDRESSES = tuple(f"{r}{c}" for r in ROWS for c in range(1, 17))
TRACKS = ("i", "u", "us")
SUBLANES = ("identity", "sequence", "neighbors", "symmetry", "cross_core")
EXPLORERS = ("forward", "reverse", "transform")

def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))

def digest(value):
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()

def egg_cycle(memory=None, cycles=1):
    """Synchronous bounded feedback; historical glyph meanings never invented."""
    if not isinstance(cycles,int) or not 0 <= cycles <= 256:
        raise ValueError("cycles must be an integer from 0 to 256")
    cells = dict.fromkeys(ADDRESSES, ".")
    for address, glyph in (memory or {}).items():
        if address not in cells or not isinstance(glyph, str) or not glyph:
            raise ValueError("invalid glyph")
        cells[address] = glyph
    # The three tracks interact through snapshots from the preceding round only.
    egg = {"zero": 0, "i": {}, "u": {}, "us": {}}
    ledger = []
    for cycle in range(cycles):
        prev = egg
        chars = {a: g for a,g in cells.items() if g != "."}
        next_i = {"characters": chars,
                  "intent": prev["us"].get("next_intent", "unassigned"),
                  "consequence_context": prev["u"].get("signal", "unknown")}
        # No physical harmony/resonance scores without observed data.
        next_u = {"identity_digest": digest(next_i["characters"]),
                  "prior_lifecycle": prev["us"].get("phase", "creation"),
                  "signal": "unknown"}
        phases = ("creation", "life", "death", "recycle", "repeat")
        phase = phases[cycle % len(phases)]
        next_us = {"phase": phase,
                   "identity_digest": digest(next_i),
                   "consequence_digest": digest(next_u),
                   "next_intent": "unassigned"}
        egg = {"zero": 0, "i": next_i, "u": next_u, "us": next_us}
        # One logical read at each glyph per sublane/explorer.
        observations = 256 * len(SUBLANES) * len(EXPLORERS)
        ledger.append({"cycle": cycle, "egg": egg, "observations": observations,
                       "parent": ledger[-1]["digest"] if ledger else None})
        ledger[-1]["digest"] = digest(ledger[-1])
    return {"configuration":{"cores":4,"lanes":120,"sublanes_per_lane":5,
            "explorers_per_sublane":3,"tracks":TRACKS,"zero":0},
            "egg":egg,"ledger":ledger,"head":ledger[-1]["digest"] if ledger else None}

if __name__=="__main__":
    r=egg_cycle(cycles=1)
    print(canonical({"configuration":r["configuration"],"egg":r["egg"],"head":r["head"]}))
