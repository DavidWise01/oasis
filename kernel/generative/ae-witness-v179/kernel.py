#!/usr/bin/env python3
"""OaSIs AE Witness-Generative Kernel v179.

Append-only descendant of AE Hierarchical Generative Kernel v178.

v179 does not choose the still-unbound 10-label -> 10-orbit permutation.
Instead it adds a deterministic, hash-linked witness receipt that can be
verified locally by NOM/NOMCOG while both repositories retain independent
authority.

Semantic scope: user-defined symbolic/isomorphic software model.
No external physical-law claim is made by this runtime.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Optional
import argparse
import importlib.util
import json
import sys

VERSION = "v179"
STATUS = "GENERATIVE / WITNESSED / APPEND-ONLY / SEALED"
RECEIPT_SCHEMA = "oasis.ae.witness.receipt.v179"

HERE = Path(__file__).resolve().parent
PARENT_PATH = HERE.parent / "ae-hierarchical-v178" / "kernel.py"

OASIS_PARENT_COMMIT = "094bcff5f9ff9dae2fc1baf22ed4597567a3bf28"
NOM_TETHER_COMMIT = "fa166428fba73d34979954296968c5dd00950354"

NOM_REPO = "DavidWise01/nom"
NOM_POSI = "Posi v00.01"
NOM_STABLE_REF = "posi-v00.01"
NOM_SEALED_PARENT_COMMIT = "aac18870dfbc12a20bd7b1e220336286ac887873"
NOM_EXECUTABLE_CAPSTONE_SHA256 = "feb8194640e32be06827e42ce755fcd7408af73d4aa592fe9ff632704c3ff427"
NOM_MANIFEST_SHA256 = "ebb5588a22c644f13f674d9c11cf476d16ac8847e8c8196d89f2ff21c108ffd8"
NOM_IDENTITY_ANCHOR = 17
NOM_PROVENANCE_ANCHOR = 131
NOM_NETWORK = "disabled"


def _load_parent():
    spec = importlib.util.spec_from_file_location("oasis_ae_v178", PARENT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load v178 parent from {PARENT_PATH}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


PARENT = _load_parent()


@dataclass(frozen=True)
class WitnessReceipt:
    schema: str
    kernel_version: str
    source_repo: str
    source_parent_commit: str
    source_frozen_canon_sha256: str
    source_state_id: str
    source_state_seal: str
    source_state_json_sha256: str
    source_generation: int
    source_point: tuple[int, int]
    source_orbit_class: int
    source_lane_label: str
    source_lane_class_binding: int | None
    binding_status: str
    source_control: str
    source_halted: bool
    source_polarity: str
    nom_repo: str
    nom_tether_commit: str
    nom_posi: str
    nom_stable_ref: str
    nom_sealed_parent_commit: str
    nom_executable_capstone_sha256: str
    nom_manifest_sha256: str
    nom_identity_anchor: int
    nom_provenance_anchor: int
    nom_network: str
    previous_receipt_id: str | None
    previous_receipt_seal: str | None
    receipt_id: str
    seal: str


def _state_json_sha256(state) -> str:
    return PARENT.sha256_bytes(PARENT.canonical_json(PARENT.state_to_dict(state)))


def _receipt_core(
    state,
    previous: Optional[WitnessReceipt],
) -> dict:
    if not PARENT.verify_state(state):
        raise ValueError("source state seal is invalid")
    if previous is not None and not verify_receipt(previous):
        raise ValueError("previous receipt is invalid")

    binding = state.lane_class_binding
    if binding is None:
        binding_status = "UNBOUND"
    else:
        if binding != state.orbit_class:
            raise ValueError("bound lane class does not match source orbit class")
        binding_status = "BOUND"

    return {
        "schema": RECEIPT_SCHEMA,
        "kernel_version": VERSION,
        "source_repo": "DavidWise01/oasis",
        "source_parent_commit": OASIS_PARENT_COMMIT,
        "source_frozen_canon_sha256": PARENT.FROZEN_CANON_SHA256,
        "source_state_id": state.state_id,
        "source_state_seal": state.seal,
        "source_state_json_sha256": _state_json_sha256(state),
        "source_generation": state.generation,
        "source_point": list(state.point),
        "source_orbit_class": state.orbit_class,
        "source_lane_label": state.lane_label,
        "source_lane_class_binding": binding,
        "binding_status": binding_status,
        "source_control": state.control,
        "source_halted": state.halted,
        "source_polarity": state.polarity,
        "nom_repo": NOM_REPO,
        "nom_tether_commit": NOM_TETHER_COMMIT,
        "nom_posi": NOM_POSI,
        "nom_stable_ref": NOM_STABLE_REF,
        "nom_sealed_parent_commit": NOM_SEALED_PARENT_COMMIT,
        "nom_executable_capstone_sha256": NOM_EXECUTABLE_CAPSTONE_SHA256,
        "nom_manifest_sha256": NOM_MANIFEST_SHA256,
        "nom_identity_anchor": NOM_IDENTITY_ANCHOR,
        "nom_provenance_anchor": NOM_PROVENANCE_ANCHOR,
        "nom_network": NOM_NETWORK,
        "previous_receipt_id": None if previous is None else previous.receipt_id,
        "previous_receipt_seal": None if previous is None else previous.seal,
    }


def make_receipt(state, previous: Optional[WitnessReceipt] = None) -> WitnessReceipt:
    core = _receipt_core(state, previous)
    receipt_id = "wr179:" + PARENT.sha256_bytes(
        b"receipt-id|" + PARENT.canonical_json(core)
    )[:24]
    payload = {**core, "receipt_id": receipt_id}
    seal = PARENT.sha256_bytes(PARENT.canonical_json(payload))
    return WitnessReceipt(
        **{
            **payload,
            "source_point": tuple(payload["source_point"]),
            "seal": seal,
        }
    )


def _receipt_core_from_receipt(receipt: WitnessReceipt) -> dict:
    data = asdict(receipt)
    data["source_point"] = list(receipt.source_point)
    data.pop("receipt_id")
    data.pop("seal")
    return data


def verify_receipt(receipt: WitnessReceipt) -> bool:
    if receipt.schema != RECEIPT_SCHEMA or receipt.kernel_version != VERSION:
        return False
    if receipt.source_repo != "DavidWise01/oasis":
        return False
    if receipt.source_parent_commit != OASIS_PARENT_COMMIT:
        return False
    if receipt.source_frozen_canon_sha256 != PARENT.FROZEN_CANON_SHA256:
        return False
    if receipt.nom_repo != NOM_REPO or receipt.nom_tether_commit != NOM_TETHER_COMMIT:
        return False
    if receipt.nom_posi != NOM_POSI or receipt.nom_stable_ref != NOM_STABLE_REF:
        return False
    if receipt.nom_sealed_parent_commit != NOM_SEALED_PARENT_COMMIT:
        return False
    if receipt.nom_executable_capstone_sha256 != NOM_EXECUTABLE_CAPSTONE_SHA256:
        return False
    if receipt.nom_manifest_sha256 != NOM_MANIFEST_SHA256:
        return False
    if receipt.nom_identity_anchor != NOM_IDENTITY_ANCHOR:
        return False
    if receipt.nom_provenance_anchor != NOM_PROVENANCE_ANCHOR:
        return False
    if receipt.nom_network != "disabled":
        return False
    if receipt.binding_status not in ("UNBOUND", "BOUND"):
        return False
    if receipt.binding_status == "UNBOUND":
        if receipt.source_lane_class_binding is not None:
            return False
    else:
        if receipt.source_lane_class_binding != receipt.source_orbit_class:
            return False

    core = _receipt_core_from_receipt(receipt)
    expected_id = "wr179:" + PARENT.sha256_bytes(
        b"receipt-id|" + PARENT.canonical_json(core)
    )[:24]
    if receipt.receipt_id != expected_id:
        return False
    payload = {**core, "receipt_id": receipt.receipt_id}
    expected_seal = PARENT.sha256_bytes(PARENT.canonical_json(payload))
    return receipt.seal == expected_seal


def receipt_to_dict(receipt: WitnessReceipt) -> dict:
    data = asdict(receipt)
    data["source_point"] = list(receipt.source_point)
    return data


def receipt_from_dict(data: dict) -> WitnessReceipt:
    return WitnessReceipt(
        **{
            **data,
            "source_point": tuple(data["source_point"]),
        }
    )


def verify_chain(receipts: list[WitnessReceipt]) -> bool:
    if not receipts:
        return True
    for i, receipt in enumerate(receipts):
        if not verify_receipt(receipt):
            return False
        if i == 0:
            if receipt.previous_receipt_id is not None or receipt.previous_receipt_seal is not None:
                return False
        else:
            prev = receipts[i - 1]
            if receipt.previous_receipt_id != prev.receipt_id:
                return False
            if receipt.previous_receipt_seal != prev.seal:
                return False
    return True


def emit_receipt(receipt: WitnessReceipt, out_dir: Path) -> Path:
    if not verify_receipt(receipt):
        raise ValueError("refusing to emit invalid receipt")
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{receipt.source_generation:06d}_{receipt.receipt_id.replace(':', '_')}.json"
    data = json.dumps(
        receipt_to_dict(receipt),
        sort_keys=True,
        indent=2,
        ensure_ascii=False,
    ).encode("utf-8") + b"\n"
    if path.exists():
        existing = path.read_bytes()
        if existing != data:
            raise RuntimeError(f"append-only receipt collision: {path}")
        return path
    path.write_bytes(data)
    return path


def nom_bridge_packet(receipt: WitnessReceipt) -> dict:
    if not verify_receipt(receipt):
        raise ValueError("invalid receipt")
    return {
        "schema": "nom.nomcog.oasis.witness.packet.v179",
        "network": "disabled",
        "identity_anchor": NOM_IDENTITY_ANCHOR,
        "provenance_anchor": NOM_PROVENANCE_ANCHOR,
        "posi": NOM_POSI,
        "posi_stable_ref": NOM_STABLE_REF,
        "oasis_receipt": receipt_to_dict(receipt),
    }


def demo() -> dict:
    PARENT.verify_frozen_canon()
    state0 = PARENT.genesis(
        PARENT.Genesis("0.s0.0", (0, 0), 0, "-"),
        lane_label="plank0",
    )
    events = [
        PARENT.Event("dot:|<.>|", "aaL", -1),
        PARENT.Event("mirror:|)>.<(|", "bbL", 0),
        PARENT.Event("slot:cc", "ccL", +1),
        PARENT.Event("terminal", "plank0", 0, PARENT.STOP_TOKEN),
    ]
    states = [state0]
    for event in events:
        states.append(PARENT.generate_child(states[-1], event))

    receipts: list[WitnessReceipt] = []
    previous = None
    for state in states:
        receipt = make_receipt(state, previous)
        receipts.append(receipt)
        previous = receipt

    if not verify_chain(receipts):
        raise RuntimeError("demo receipt chain failed verification")

    return {
        "status": "0e / AE WITNESS-GENERATIVE v179 DEMO PASS",
        "version": VERSION,
        "parent": "v178",
        "receipt_count": len(receipts),
        "binding_status": [r.binding_status for r in receipts],
        "final_halted": receipts[-1].source_halted,
        "final_control": receipts[-1].source_control,
        "final_receipt_id": receipts[-1].receipt_id,
        "final_receipt_seal": receipts[-1].seal,
        "receipts": [receipt_to_dict(r) for r in receipts],
    }


def _main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify-canon", action="store_true")
    parser.add_argument("--demo", action="store_true")
    parser.add_argument("--emit-dir", type=Path)
    args = parser.parse_args(argv)

    if args.verify_canon:
        print(PARENT.verify_frozen_canon())

    if args.demo:
        result = demo()
        if args.emit_dir:
            previous = None
            for data in result["receipts"]:
                receipt = receipt_from_dict(data)
                if previous is not None:
                    if receipt.previous_receipt_id != previous.receipt_id:
                        raise RuntimeError("demo chain mismatch")
                emit_receipt(receipt, args.emit_dir)
                previous = receipt
        print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(sys.argv[1:]))
