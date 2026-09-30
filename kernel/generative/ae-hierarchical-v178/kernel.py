#!/usr/bin/env python3
"""OaSIs AE Hierarchical Generative Kernel v178.

Append-only descendant of the frozen AE Generative-First Kernel v92.

This runtime:
- verifies the frozen v92 CANON.json before generation;
- never edits the frozen parent/canon;
- generates deterministic child states from explicit events;
- preserves the 10x10 / (-2,+3) lane geometry;
- preserves /0/0 as a STOP token, not arithmetic division;
- preserves the bidirectional polarity seal - <-> +;
- leaves the 10 lane-label -> 10 orbit-class permutation explicit/parametric.

Semantic scope: user-defined symbolic/isomorphic software model.
No external physical-law claim is made by this runtime.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from fractions import Fraction
from pathlib import Path
from typing import Mapping, Optional
import argparse
import hashlib
import json
import sys

VERSION = "v178"
STATUS = "GENERATIVE / APPEND-ONLY / SEALED"
FROZEN_PARENT = "ae-generative-first-v92"
FROZEN_CANON_SHA256 = "8f2be8951098c7e1764c3c0f5bba982fb3fd8c71f094924b79d0172a313a7bf8"

FIELD_W = 10
FIELD_H = 10
SIGNED_STEP = (-2, +3)
DOT_MULTIPLICITY = 2 ** 3
STOP_TOKEN = "/0/0"
POLARITIES = ("-", "+")
CARRIER_SLOTS = (
    "aaL", "bbL", "ccL", "ddL",
    "ddR", "ccR", "bbR", "aaR",
)
LANE_LABELS = CARRIER_SLOTS + ("plank0", "plank1")
MIRROR_SLOT = {
    "aaL": "aaR", "bbL": "bbR", "ccL": "ccR", "ddL": "ddR",
    "ddR": "ddL", "ccR": "ccL", "bbR": "bbL", "aaR": "aaL",
}
MIRROR_DEPTH = {
    "aaL": 0, "bbL": 1, "ccL": 2, "ddL": 3,
    "ddR": 3, "ccR": 2, "bbR": 1, "aaR": 0,
}
ELEMENT_ENDPOINTS = {1: "h::{au}", 255: "u::{ag}"}
FACTORIAL_PREFIX = Fraction(11200, 13)

HERE = Path(__file__).resolve().parent
DEFAULT_FROZEN_CANON = (
    HERE.parent.parent / "frozen" / "ae-generative-first-v92" / "CANON.json"
)

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def canonical_json(obj) -> bytes:
    return json.dumps(
        obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")

def verify_frozen_canon(path: Path = DEFAULT_FROZEN_CANON) -> str:
    raw = path.read_bytes()
    actual = sha256_bytes(raw)
    if actual != FROZEN_CANON_SHA256:
        raise RuntimeError(
            f"FROZEN CANON HASH MISMATCH: {actual} != {FROZEN_CANON_SHA256}"
        )
    return actual

def normalize_point(point: tuple[int, int]) -> tuple[int, int]:
    return (point[0] % FIELD_W, point[1] % FIELD_H)

def step_point(point: tuple[int, int]) -> tuple[int, int]:
    x, y = normalize_point(point)
    dx, dy = SIGNED_STEP
    return ((x + dx) % FIELD_W, (y + dy) % FIELD_H)

def invariant_class(point: tuple[int, int]) -> int:
    x, y = normalize_point(point)
    return (3 * x + 2 * y) % 10

def orbit(seed: tuple[int, int]) -> tuple[tuple[int, int], ...]:
    p = normalize_point(seed)
    out: list[tuple[int, int]] = []
    seen: set[tuple[int, int]] = set()
    while p not in seen:
        seen.add(p)
        out.append(p)
        p = step_point(p)
    return tuple(out)

def field_orbit_partition() -> dict[int, tuple[tuple[int, int], ...]]:
    """Return the exact ten invariant classes on the 10x10 field."""
    classes: dict[int, list[tuple[int, int]]] = {i: [] for i in range(10)}
    for x in range(FIELD_W):
        for y in range(FIELD_H):
            classes[invariant_class((x, y))].append((x, y))
    out: dict[int, tuple[tuple[int, int], ...]] = {}
    for cls, pts in classes.items():
        if len(pts) != 10:
            raise AssertionError(f"class {cls} has {len(pts)} cells")
        seed = min(pts)
        o = orbit(seed)
        if len(o) != 10 or set(o) != set(pts):
            raise AssertionError(f"class {cls} does not equal one walker orbit")
        out[cls] = o
    return out

def bind_polarity(polarity: str) -> str:
    if polarity == "-":
        return "+"
    if polarity == "+":
        return "-"
    raise ValueError("polarity must be '-' or '+'")

def mirror_slot(slot: str) -> str:
    try:
        return MIRROR_SLOT[slot]
    except KeyError as exc:
        raise ValueError(f"unknown carrier slot: {slot}") from exc

def settle_transient_zero(plank: int) -> str:
    if plank == 0:
        return ".5"
    if plank == 1:
        return "1"
    raise ValueError("plank must be 0 or 1")

def gradient_lift(n: int, gradient: int) -> int:
    if gradient not in (-1, 0, +1):
        raise ValueError("gradient must be -1, 0, or +1")
    return n + gradient + 1

def factorial_prefix() -> Fraction:
    return FACTORIAL_PREFIX

@dataclass(frozen=True)
class Genesis:
    seed_literal: str
    point: tuple[int, int]
    plank: int
    polarity: str

@dataclass(frozen=True)
class Event:
    payload: str
    lane_label: str
    gradient: int
    control: str = "RUN"

@dataclass(frozen=True)
class State:
    version: str
    generation: int
    state_id: str
    parent_id: str | None
    point: tuple[int, int]
    orbit_class: int
    lane_label: str
    lane_class_binding: int | None
    plank: int
    settled_zero: str
    polarity: str
    hierarchy_n: int
    control: str
    halted: bool
    parent_seal: str | None
    seal: str

def _state_payload_without_seal(
    *,
    generation: int,
    state_id: str,
    parent_id: str | None,
    point: tuple[int, int],
    orbit_cls: int,
    lane_label: str,
    lane_class_binding: int | None,
    plank: int,
    settled_zero: str,
    polarity: str,
    hierarchy_n: int,
    control: str,
    halted: bool,
    parent_seal: str | None,
) -> dict:
    return {
        "version": VERSION,
        "generation": generation,
        "state_id": state_id,
        "parent_id": parent_id,
        "point": list(point),
        "orbit_class": orbit_cls,
        "lane_label": lane_label,
        "lane_class_binding": lane_class_binding,
        "plank": plank,
        "settled_zero": settled_zero,
        "polarity": polarity,
        "hierarchy_n": hierarchy_n,
        "control": control,
        "halted": halted,
        "parent_seal": parent_seal,
    }

def _make_state(**kwargs) -> State:
    payload = _state_payload_without_seal(**kwargs)
    seal = sha256_bytes(canonical_json(payload))
    return State(
        version=VERSION,
        generation=payload["generation"],
        state_id=payload["state_id"],
        parent_id=payload["parent_id"],
        point=tuple(payload["point"]),
        orbit_class=payload["orbit_class"],
        lane_label=payload["lane_label"],
        lane_class_binding=payload["lane_class_binding"],
        plank=payload["plank"],
        settled_zero=payload["settled_zero"],
        polarity=payload["polarity"],
        hierarchy_n=payload["hierarchy_n"],
        control=payload["control"],
        halted=payload["halted"],
        parent_seal=payload["parent_seal"],
        seal=seal,
    )

def _validate_lane_binding(
    lane_label: str,
    orbit_cls: int,
    lane_binding: Optional[Mapping[str, int]],
) -> int | None:
    if lane_label not in LANE_LABELS:
        raise ValueError(f"unknown lane label: {lane_label}")
    if lane_binding is None:
        return None

    if set(lane_binding.keys()) != set(LANE_LABELS):
        raise ValueError("lane binding must bind exactly all 10 lane labels")
    vals = list(lane_binding.values())
    if sorted(vals) != list(range(10)):
        raise ValueError("lane binding must be a bijection onto orbit classes 0..9")

    bound = lane_binding[lane_label]
    if bound != orbit_cls:
        raise ValueError(
            f"lane binding mismatch: {lane_label}->{bound}, point is class {orbit_cls}"
        )
    return bound

def genesis(
    spec: Genesis,
    *,
    lane_label: str = "plank0",
    lane_binding: Optional[Mapping[str, int]] = None,
) -> State:
    if spec.plank not in (0, 1):
        raise ValueError("plank must be 0 or 1")
    if spec.polarity not in POLARITIES:
        raise ValueError("polarity must be '-' or '+'")

    point = normalize_point(spec.point)
    cls = invariant_class(point)
    binding = _validate_lane_binding(lane_label, cls, lane_binding)

    seed = canonical_json({
        "version": VERSION,
        "frozen_parent": FROZEN_PARENT,
        "frozen_canon_sha256": FROZEN_CANON_SHA256,
        "seed_literal": spec.seed_literal,
        "point": point,
        "plank": spec.plank,
        "polarity": spec.polarity,
        "lane_label": lane_label,
        "orbit_class": cls,
        "lane_binding": binding,
    })
    state_id = "v178:" + sha256_bytes(b"genesis|" + seed)[:24]
    return _make_state(
        generation=0,
        state_id=state_id,
        parent_id=None,
        point=point,
        orbit_cls=cls,
        lane_label=lane_label,
        lane_class_binding=binding,
        plank=spec.plank,
        settled_zero=settle_transient_zero(spec.plank),
        polarity=spec.polarity,
        hierarchy_n=0,
        control="RUN",
        halted=False,
        parent_seal=None,
    )

def generate_child(
    parent: State,
    event: Event,
    *,
    lane_binding: Optional[Mapping[str, int]] = None,
) -> State:
    if parent.halted:
        raise RuntimeError("cannot generate from a halted parent")

    if event.gradient not in (-1, 0, +1):
        raise ValueError("gradient must be -1, 0, or +1")

    halted = event.control == STOP_TOKEN
    if event.control not in ("RUN", STOP_TOKEN):
        raise ValueError("control must be RUN or /0/0")

    next_point = parent.point if halted else step_point(parent.point)
    next_cls = invariant_class(next_point)
    binding = _validate_lane_binding(event.lane_label, next_cls, lane_binding)
    next_plank = parent.plank
    next_polarity = parent.polarity if halted else bind_polarity(parent.polarity)
    next_n = parent.hierarchy_n if halted else gradient_lift(
        parent.hierarchy_n, event.gradient
    )

    seed = canonical_json({
        "version": VERSION,
        "parent_id": parent.state_id,
        "parent_seal": parent.seal,
        "generation": parent.generation + 1,
        "payload": event.payload,
        "lane_label": event.lane_label,
        "gradient": event.gradient,
        "control": event.control,
        "next_point": next_point,
        "orbit_class": next_cls,
        "lane_binding": binding,
        "plank": next_plank,
        "polarity": next_polarity,
        "hierarchy_n": next_n,
    })
    state_id = "v178:" + sha256_bytes(b"child|" + seed)[:24]

    return _make_state(
        generation=parent.generation + 1,
        state_id=state_id,
        parent_id=parent.state_id,
        point=next_point,
        orbit_cls=next_cls,
        lane_label=event.lane_label,
        lane_class_binding=binding,
        plank=next_plank,
        settled_zero=settle_transient_zero(next_plank),
        polarity=next_polarity,
        hierarchy_n=next_n,
        control=event.control,
        halted=halted,
        parent_seal=parent.seal,
    )

def state_to_dict(state: State) -> dict:
    d = asdict(state)
    d["point"] = list(state.point)
    return d

def emit_state(state: State, out_dir: Path) -> Path:
    """Append-only emission.

    Existing identical state file => idempotent success.
    Existing different bytes => hard refusal.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{state.generation:06d}_{state.state_id.replace(':', '_')}.json"
    data = json.dumps(
        state_to_dict(state), sort_keys=True, indent=2, ensure_ascii=False
    ).encode("utf-8") + b"\n"

    if path.exists():
        existing = path.read_bytes()
        if existing != data:
            raise RuntimeError(f"append-only collision: {path}")
        return path

    path.write_bytes(data)
    return path

def verify_state(state: State) -> bool:
    payload = _state_payload_without_seal(
        generation=state.generation,
        state_id=state.state_id,
        parent_id=state.parent_id,
        point=state.point,
        orbit_cls=state.orbit_class,
        lane_label=state.lane_label,
        lane_class_binding=state.lane_class_binding,
        plank=state.plank,
        settled_zero=state.settled_zero,
        polarity=state.polarity,
        hierarchy_n=state.hierarchy_n,
        control=state.control,
        halted=state.halted,
        parent_seal=state.parent_seal,
    )
    return state.seal == sha256_bytes(canonical_json(payload))

def demo() -> dict:
    partition = field_orbit_partition()
    g = genesis(Genesis("0.s0.0", (0, 0), 0, "-"), lane_label="plank0")
    events = [
        Event("dot:|<.>|", "aaL", -1),
        Event("mirror:|)>.<(|", "bbL", 0),
        Event("slot:cc", "ccL", +1),
        Event("terminal", "plank0", 0, STOP_TOKEN),
    ]
    states = [g]
    for e in events:
        states.append(generate_child(states[-1], e))
    return {
        "status": "0e / GENERATIVE v178 DEMO PASS",
        "version": VERSION,
        "frozen_parent": FROZEN_PARENT,
        "frozen_canon_sha256": FROZEN_CANON_SHA256,
        "field_orbits": len(partition),
        "cells": sum(len(v) for v in partition.values()),
        "factorial_prefix": f"{FACTORIAL_PREFIX.numerator}/{FACTORIAL_PREFIX.denominator}",
        "states": [state_to_dict(s) for s in states],
    }

def _main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify-canon", action="store_true")
    parser.add_argument("--demo", action="store_true")
    parser.add_argument("--emit-dir", type=Path)
    args = parser.parse_args(argv)

    if args.verify_canon:
        print(verify_frozen_canon())

    if args.demo:
        result = demo()
        if args.emit_dir:
            for state_dict in result["states"]:
                state = State(
                    **{
                        **state_dict,
                        "point": tuple(state_dict["point"]),
                    }
                )
                emit_state(state, args.emit_dir)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    raise SystemExit(_main(sys.argv[1:]))
