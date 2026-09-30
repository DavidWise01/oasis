#!/usr/bin/env python3
from dataclasses import replace
from pathlib import Path
import json
import tempfile

import kernel


def test_all() -> dict:
    parent = kernel.PARENT

    # Frozen v92 remains the root trust anchor through v178.
    assert parent.verify_frozen_canon() == parent.FROZEN_CANON_SHA256

    # v179 must not mutate or silently choose the lane permutation.
    state0 = parent.genesis(
        parent.Genesis("0.s0.0", (0, 0), 0, "-"),
        lane_label="plank0",
    )
    r0a = kernel.make_receipt(state0)
    r0b = kernel.make_receipt(state0)
    assert r0a == r0b
    assert r0a.binding_status == "UNBOUND"
    assert r0a.source_lane_class_binding is None
    assert r0a.source_orbit_class == 0
    assert kernel.verify_receipt(r0a)

    # A valid explicit bijection may bind a lane; no implicit map is invented.
    binding = {label: i for i, label in enumerate(parent.LANE_LABELS)}
    bound_state = parent.genesis(
        parent.Genesis("0.s0.0", (0, 0), 0, "-"),
        lane_label="aaL",
        lane_binding=binding,
    )
    rb = kernel.make_receipt(bound_state)
    assert rb.binding_status == "BOUND"
    assert rb.source_lane_class_binding == rb.source_orbit_class == 0
    assert kernel.verify_receipt(rb)

    # Invalid/non-bijective maps remain rejected by the parent gate.
    bad = {label: 0 for label in parent.LANE_LABELS}
    failed = False
    try:
        parent.genesis(
            parent.Genesis("0.s0.0", (0, 0), 0, "-"),
            lane_label="aaL",
            lane_binding=bad,
        )
    except ValueError:
        failed = True
    assert failed

    # Generate a deterministic child receipt and chain it to the genesis receipt.
    event = parent.Event("dot:|<.>|", "aaL", -1)
    child = parent.generate_child(state0, event)
    r1a = kernel.make_receipt(child, r0a)
    r1b = kernel.make_receipt(child, r0a)
    assert r1a == r1b
    assert r1a.previous_receipt_id == r0a.receipt_id
    assert r1a.previous_receipt_seal == r0a.seal
    assert kernel.verify_chain([r0a, r1a])

    # NOM/Posi anchors are carried without enabling network access.
    assert r1a.nom_identity_anchor == 17
    assert r1a.nom_provenance_anchor == 131
    assert r1a.nom_network == "disabled"
    packet = kernel.nom_bridge_packet(r1a)
    assert packet["network"] == "disabled"
    assert packet["identity_anchor"] == 17
    assert packet["provenance_anchor"] == 131
    assert packet["oasis_receipt"]["receipt_id"] == r1a.receipt_id

    # Tampering with any receipt field breaks the deterministic seal.
    tampered = replace(r1a, source_orbit_class=(r1a.source_orbit_class + 1) % 10)
    assert not kernel.verify_receipt(tampered)

    tampered_anchor = replace(r1a, nom_identity_anchor=18)
    assert not kernel.verify_receipt(tampered_anchor)

    # /0/0 remains STOP and the terminal state can be witnessed.
    stop_state = parent.generate_child(
        child,
        parent.Event("terminal", "plank0", 0, parent.STOP_TOKEN),
    )
    stop_receipt = kernel.make_receipt(stop_state, r1a)
    assert stop_receipt.source_halted is True
    assert stop_receipt.source_control == parent.STOP_TOKEN
    assert kernel.verify_chain([r0a, r1a, stop_receipt])

    # Append-only emission is idempotent for identical bytes and refuses mutation.
    with tempfile.TemporaryDirectory() as td:
        out = Path(td)
        p = kernel.emit_receipt(r1a, out)
        original = p.read_bytes()
        p2 = kernel.emit_receipt(r1a, out)
        assert p2 == p
        assert p.read_bytes() == original

        p.write_bytes(b"tampered\n")
        failed = False
        try:
            kernel.emit_receipt(r1a, out)
        except RuntimeError:
            failed = True
        assert failed

    demo = kernel.demo()
    assert demo["status"] == "0e / AE WITNESS-GENERATIVE v179 DEMO PASS"
    assert demo["receipt_count"] == 5
    assert demo["binding_status"] == ["UNBOUND"] * 5
    assert demo["final_halted"] is True
    assert demo["final_control"] == parent.STOP_TOKEN

    return {
        "status": "0e / AE WITNESS-GENERATIVE v179 PASS",
        "parent": "v178",
        "frozen_canon_sha256": parent.FROZEN_CANON_SHA256,
        "tests": {
            "deterministic_receipt": "PASS",
            "explicit_lane_bijection_gate": "PASS",
            "unbound_mapping_preserved": "PASS",
            "hash_linked_receipt_chain": "PASS",
            "nom_posi_anchors": "PASS",
            "network_disabled": "PASS",
            "tamper_rejection": "PASS",
            "terminal_stop_receipt": "PASS",
            "append_only_emission": "PASS",
            "demo": "PASS",
        },
    }


if __name__ == "__main__":
    print(json.dumps(test_all(), indent=2))
