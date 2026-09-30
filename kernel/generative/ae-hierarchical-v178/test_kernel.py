#!/usr/bin/env python3
from pathlib import Path
from fractions import Fraction
import json
import tempfile

import kernel

def test_all() -> dict:
    # Frozen trust anchor is verified from the real repository parent.
    canon_hash = kernel.verify_frozen_canon()
    assert canon_hash == kernel.FROZEN_CANON_SHA256

    # Fixed constants / hierarchy.
    assert kernel.FIELD_W * kernel.FIELD_H == 100
    assert kernel.DOT_MULTIPLICITY == 8
    assert len(kernel.CARRIER_SLOTS) == 8
    assert len(kernel.LANE_LABELS) == 10
    assert kernel.factorial_prefix() == Fraction(11200, 13)

    # Mirror is an involution with preserved depth.
    for slot in kernel.CARRIER_SLOTS:
        mirrored = kernel.mirror_slot(slot)
        assert kernel.mirror_slot(mirrored) == slot
        assert kernel.MIRROR_DEPTH[mirrored] == kernel.MIRROR_DEPTH[slot]

    # Exact 10x10 partition by the (-2,+3) walker.
    partition = kernel.field_orbit_partition()
    assert set(partition) == set(range(10))
    assert all(len(o) == 10 for o in partition.values())
    all_cells = [p for o in partition.values() for p in o]
    assert len(all_cells) == 100
    assert len(set(all_cells)) == 100
    assert set(all_cells) == {(x,y) for x in range(10) for y in range(10)}

    # Invariant class is preserved by the signed step.
    for x in range(10):
        for y in range(10):
            p = (x,y)
            assert kernel.invariant_class(kernel.step_point(p)) == kernel.invariant_class(p)

    # Plank and gradient rules.
    assert kernel.settle_transient_zero(0) == ".5"
    assert kernel.settle_transient_zero(1) == "1"
    assert kernel.gradient_lift(13, -1) == 13
    assert kernel.gradient_lift(13, 0) == 14
    assert kernel.gradient_lift(13, +1) == 15

    # Bidirectional seal.
    assert kernel.bind_polarity("-") == "+"
    assert kernel.bind_polarity("+") == "-"
    assert kernel.bind_polarity(kernel.bind_polarity("-")) == "-"

    # Deterministic genesis + deterministic generation.
    spec = kernel.Genesis("0.s0.0", (0,0), 0, "-")
    g1 = kernel.genesis(spec, lane_label="plank0")
    g2 = kernel.genesis(spec, lane_label="plank0")
    assert g1 == g2
    assert kernel.verify_state(g1)

    e = kernel.Event("dot:|<.>|", "aaL", -1)
    c1 = kernel.generate_child(g1, e)
    c2 = kernel.generate_child(g2, e)
    assert c1 == c2
    assert c1.parent_id == g1.state_id
    assert c1.parent_seal == g1.seal
    assert c1.point == kernel.step_point(g1.point)
    assert c1.polarity == "+"
    assert kernel.verify_state(c1)

    # Lane-class assignment stays explicit. Invalid/non-bijective maps are refused.
    bad = {label: 0 for label in kernel.LANE_LABELS}
    failed = False
    try:
        kernel.genesis(spec, lane_label="plank0", lane_binding=bad)
    except ValueError:
        failed = True
    assert failed

    # A valid bijection is accepted only when it agrees with the mathematical orbit class.
    # Assign labels so plank0 gets class 0, which matches genesis point (0,0).
    binding = {label: i for i, label in enumerate(kernel.LANE_LABELS)}
    gb = kernel.genesis(spec, lane_label="aaL", lane_binding=binding)
    assert gb.lane_class_binding == 0

    # /0/0 is STOP, not division.
    stop = kernel.Event("terminal", "plank0", 0, kernel.STOP_TOKEN)
    halted = kernel.generate_child(c1, stop)
    assert halted.halted is True
    assert halted.control == kernel.STOP_TOKEN
    assert halted.point == c1.point
    assert halted.polarity == c1.polarity
    assert kernel.verify_state(halted)

    failed = False
    try:
        kernel.generate_child(halted, e)
    except RuntimeError:
        failed = True
    assert failed, "halted state must not generate children"

    # Append-only emission: identical re-emission is idempotent, mutation is refused.
    with tempfile.TemporaryDirectory() as td:
        out = Path(td)
        p = kernel.emit_state(c1, out)
        original = p.read_bytes()
        p2 = kernel.emit_state(c1, out)
        assert p2 == p
        assert p.read_bytes() == original

        p.write_bytes(b"tampered\n")
        failed = False
        try:
            kernel.emit_state(c1, out)
        except RuntimeError:
            failed = True
        assert failed, "append-only collision must be refused"

    demo = kernel.demo()
    assert demo["status"] == "0e / GENERATIVE v178 DEMO PASS"
    assert demo["field_orbits"] == 10
    assert demo["cells"] == 100
    assert demo["states"][-1]["halted"] is True

    return {
        "status": "0e / AE HIERARCHICAL GENERATIVE v178 PASS",
        "canon_sha256": canon_hash,
        "tests": {
            "frozen_canon": "PASS",
            "field_partition": "10 x 10 PASS",
            "mirror_involution": "PASS",
            "plank_gradient": "PASS",
            "deterministic_generation": "PASS",
            "explicit_lane_bijection_gate": "PASS",
            "stop_terminal": "PASS",
            "bidirectional_seal": "PASS",
            "append_only_emit": "PASS",
        },
    }

if __name__ == "__main__":
    print(json.dumps(test_all(), indent=2))
