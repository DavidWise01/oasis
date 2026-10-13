#!/usr/bin/env python3
"""KET v1.5 exact seven-amplitude / three-carrier / pinned-zero register.

No numerical spectral or biological meaning is supplied by the mnemonic.
"""
from collections import Counter
import json

AMPLITUDES = ("red", "green", "blue", "orange", "purple", "green", "yellow")
CARRIERS = ("white", "black", "gray")
OPERATORS = ("gravity", "expansion", "compression", "containment", "explosion")
PINNED = 0
PREVIOUS_LITERAL = "-5 amplitudes at 0 + {{n}1.25}}^{{sqrt5}^1x1.616158^10-35}}"

def make_register():
    slots = [{"index": 0, "type": "pinned_zero", "value": PINNED}]
    slots += [{"index": i, "type": "amplitude", "color": c, "id": f"A{i}"}
              for i, c in enumerate(AMPLITUDES, 1)]
    slots += [{"index": i, "type": "carrier", "color": c, "id": f"C{i-7}"}
              for i, c in enumerate(CARRIERS, 8)]
    return {"schema": "KET/LEVIATHAN/7A3C0/v15",
            "root": "LEVIATHAN::0root",
            "nitrogen_mnemonic": "CATGNO",
            "slots": slots, "five_operators": list(OPERATORS),
            "prior_exponent_literal_unparsed": PREVIOUS_LITERAL,
            "continuous_carrier_semantics": "unassigned",
            "conditional_normalized_amplitude_manifold": "S^6 in R^7",
            "local_nodes": 250+110+6, "parent_nodes": 100*3*20+6}

def verify(s):
    assert len(s["slots"]) == 11
    assert s["slots"][0]["value"] == 0
    assert [x["color"] for x in s["slots"][1:8]] == list(AMPLITUDES)
    assert [x["color"] for x in s["slots"][8:11]] == list(CARRIERS)
    assert Counter(AMPLITUDES)["green"] == 2
    assert s["slots"][2]["id"] != s["slots"][6]["id"]
    assert len(s["five_operators"]) == 5
    assert s["local_nodes"] == 366 and s["parent_nodes"] == 6006
    assert s["root"] == "LEVIATHAN::0root"
    return True

if __name__ == "__main__":
    state = make_register()
    verify(state)
    print(json.dumps(state, indent=2))
