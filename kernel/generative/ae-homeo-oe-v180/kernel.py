#!/usr/bin/env python3
"""OaSIs AE Homeo/OE Frozen Kernel v180.

Append-only descendant of AE Witness-Generative v179.

v180 freezes the internally tested symbolic path only through oe:
    L0 0root -> L1 +G -> L2 -G = oe

It deliberately keeps the homeostatic restoring register separate from the
internal +G/-G phase register.

The first post-oe failure test is retained as an explicit xe:
    element clock 10 (NEON) vs plank/homeo clock 12
    gcd = 2, lcm = 60
but no canon rule equates an element tick with a plank/angle tick.

Semantic scope: user-defined symbolic/isomorphic software model.
No physical-law claim is made by this runtime.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Literal
import argparse
import importlib.util
import json
import math
import sys

VERSION = "v180"
STATUS = "FROZEN THROUGH oe / GENERATIVE TEST FRONTIER / APPEND-ONLY"
PARENT_VERSION = "v179"
HERE = Path(__file__).resolve().parent
PARENT_PATH = HERE.parent / "ae-witness-v179" / "kernel.py"

FROZEN_CANON_SHA256 = "8f2be8951098c7e1764c3c0f5bba982fb3fd8c71f094924b79d0172a313a7bf8"
OASIS_V179_PAGE_COMMIT = "09275db82615c1eee702292f5b69b5622ae422ee"

ROOT_LITERAL = "0root"
OE_LITERAL = "oe"
OE_MEANING = "occupied electron"

PHASE_WORD = "..||..|"
PHASE_QUANTUM_TURN = 1 / 36
PHASE_QUANTUM_DEG = 10
PLANK_STEP_PCT = 0.5
PLANK_STEP_DEG = 30
PLANKS_PER_HOME0 = 12
HOME0_WIDTH_PCT = 6.0
SECTOR_DEG = 60
SECTORS_PER_TURN = 6

ZERO_SEAM = ("-0", "+0")
MINI_PRIM_LEFT = "..||..|"
MINI_PRIM_RIGHT = "|xx||xx"
MINI_PRIM_DEG = 20
MINI_PRIMS_PER_SECTOR = 3
MINI_PRIMS_PER_TURN = 18

GRAVITY_BASELINE_G = 1.0
PUSH_LITERAL = "+1 x 10^(-36/360)"
PULL_LITERAL = "-1 x 10^(+36/360)"
PUSH_MAGNITUDE = 10 ** (-36 / 360)
PULL_MAGNITUDE = -(10 ** (+36 / 360))

GRAVITY_PAIR = {
    -1: ("-1", "-1"),
     0: ("-0", "+0"),
    +1: ("+1", "+1"),
}

POST_OE_HYDROGEN = "H upon oe"
POST_OE_NEON_INDEX = 10
POST_OE_NEON_NAME = "NEON"
POST_OE_CLOSURE_LITERAL = "10 x 10 x 10 + 2"
POST_OE_CLOSURE_VALUE = 1002
POST_OE_INGRESS = -359.494
POST_OE_EGRESS = +359.494

NEXT_XE = "xe / POST-oe ELEMENT<->PLANK CLOCK BINDING UNBOUND"


def _load_parent():
    spec = importlib.util.spec_from_file_location("oasis_ae_v179", PARENT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load v179 parent from {PARENT_PATH}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


PARENT = _load_parent()


def inverse_glyphs(word: str) -> str:
    table = str.maketrans({".": "x", "x": ".", "|": "|"})
    return word.translate(table)


def mini_prim() -> str:
    right = inverse_glyphs(MINI_PRIM_LEFT[::-1])
    if right != MINI_PRIM_RIGHT:
        raise AssertionError((right, MINI_PRIM_RIGHT))
    return f"{MINI_PRIM_LEFT} {{-0,+0}} {right}"


def homeo_branch(plank: int) -> Literal["PULL", "BALANCE", "PUSH"]:
    if plank < 0:
        return "PULL"
    if plank == 0:
        return "BALANCE"
    return "PUSH"


def homeo_force(plank: int) -> float:
    branch = homeo_branch(plank)
    if branch == "PULL":
        return PULL_MAGNITUDE
    if branch == "PUSH":
        return PUSH_MAGNITUDE
    return 0.0


def internal_phase(layer: int) -> str:
    if layer == 0:
        return "0G"
    return "+G" if layer % 2 == 1 else "-G"


@dataclass(frozen=True)
class FrozenLayer:
    layer: int
    name: str
    plank: int
    angle_deg: int
    internal_gravity_phase: str
    homeo_branch: str
    homeo_force: float
    full_gravity_baseline: float
    occupancy: str


def frozen_path() -> tuple[FrozenLayer, ...]:
    return (
        FrozenLayer(0, "L0", 0, 0, "0G", "BALANCE", 0.0, GRAVITY_BASELINE_G, ROOT_LITERAL),
        FrozenLayer(1, "L1", 1, PLANK_STEP_DEG, "+G", "PUSH", PUSH_MAGNITUDE, GRAVITY_BASELINE_G, "carrier-open"),
        FrozenLayer(2, "L2", 2, 2 * PLANK_STEP_DEG, "-G", "PUSH", PUSH_MAGNITUDE, GRAVITY_BASELINE_G, OE_LITERAL),
    )


def verify_frozen_slice() -> dict:
    frozen = PARENT.PARENT.verify_frozen_canon()
    if frozen != FROZEN_CANON_SHA256:
        raise AssertionError("unexpected frozen root")

    assert 36 * PHASE_QUANTUM_DEG == 360
    assert 3 * PHASE_QUANTUM_DEG == PLANK_STEP_DEG
    assert PLANKS_PER_HOME0 * PLANK_STEP_DEG == 360
    assert math.isclose(PLANKS_PER_HOME0 * PLANK_STEP_PCT, HOME0_WIDTH_PCT, rel_tol=0, abs_tol=1e-12)
    assert 2 * PLANK_STEP_DEG == SECTOR_DEG
    assert SECTORS_PER_TURN * SECTOR_DEG == 360
    assert MINI_PRIMS_PER_SECTOR * MINI_PRIM_DEG == SECTOR_DEG
    assert MINI_PRIMS_PER_TURN * MINI_PRIM_DEG == 360
    assert MINI_PRIMS_PER_TURN * 2 == 36
    assert math.isclose(abs(PUSH_MAGNITUDE) * abs(PULL_MAGNITUDE), 1.0, rel_tol=1e-12, abs_tol=1e-12)
    assert mini_prim() == "..||..| {-0,+0} |xx||xx"

    path = frozen_path()
    assert path[0].occupancy == ROOT_LITERAL
    assert path[1].internal_gravity_phase == "+G"
    assert path[2].internal_gravity_phase == "-G"
    assert path[2].occupancy == OE_LITERAL
    assert all(s.homeo_branch == "PUSH" for s in path[1:])
    assert path[2].homeo_branch != path[2].internal_gravity_phase

    return {
        "status": "0e / v180 FROZEN THROUGH oe PASS",
        "frozen_root_sha256": frozen,
        "phase_quantum_deg": PHASE_QUANTUM_DEG,
        "plank_step_deg": PLANK_STEP_DEG,
        "plank_step_pct": PLANK_STEP_PCT,
        "homeo_cycle_steps": PLANKS_PER_HOME0,
        "homeo_width_pct": HOME0_WIDTH_PCT,
        "mini_prim": mini_prim(),
        "mini_prim_deg": MINI_PRIM_DEG,
        "push": PUSH_MAGNITUDE,
        "pull": PULL_MAGNITUDE,
        "push_pull_abs_product": abs(PUSH_MAGNITUDE) * abs(PULL_MAGNITUDE),
        "path": [asdict(s) for s in path],
    }


def post_oe_xe_test() -> dict:
    element_clock = POST_OE_NEON_INDEX
    plank_clock = PLANKS_PER_HOME0
    common = math.lcm(element_clock, plank_clock)
    gcd = math.gcd(element_clock, plank_clock)
    return {
        "status": NEXT_XE,
        "from": OE_LITERAL,
        "known_post_oe": {
            "hydrogen_alignment": POST_OE_HYDROGEN,
            "neon_index": POST_OE_NEON_INDEX,
            "neon_name": POST_OE_NEON_NAME,
            "closure_literal": POST_OE_CLOSURE_LITERAL,
            "closure_value": POST_OE_CLOSURE_VALUE,
            "ingress": POST_OE_INGRESS,
            "egress": POST_OE_EGRESS,
        },
        "clock_test": {
            "element_modulus": element_clock,
            "plank_modulus": plank_clock,
            "gcd": gcd,
            "lcm": common,
            "existing_sector_numeric_value": SECTOR_DEG,
        },
        "reason": "LCM(10,12)=60 is arithmetic only; no frozen rule binds one element advance to one plank tick or to one angular degree/sector.",
        "required_to_close": "an explicit element<->plank/phase cadence, or another invariant that derives that cadence without unit conflation",
    }


def demo() -> dict:
    return {"version": VERSION, "status": STATUS, "frozen": verify_frozen_slice(), "next_xe": post_oe_xe_test()}


def _main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", action="store_true")
    parser.add_argument("--next-xe", action="store_true")
    parser.add_argument("--demo", action="store_true")
    args = parser.parse_args(argv)
    if args.verify:
        print(json.dumps(verify_frozen_slice(), indent=2))
    if args.next_xe:
        print(json.dumps(post_oe_xe_test(), indent=2))
    if args.demo:
        print(json.dumps(demo(), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(sys.argv[1:]))
