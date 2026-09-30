#!/usr/bin/env python3
import json
import math
import kernel

def test_all() -> dict:
    frozen = kernel.verify_frozen_slice()
    assert frozen["status"] == "0e / v180 FROZEN THROUGH oe PASS"

    assert kernel.PHASE_QUANTUM_TURN == 1 / 36
    assert kernel.PHASE_QUANTUM_DEG == 10
    assert 3 * kernel.PHASE_QUANTUM_DEG == kernel.PLANK_STEP_DEG == 30
    assert 2 * kernel.PLANK_STEP_DEG == kernel.SECTOR_DEG == 60
    assert kernel.PLANKS_PER_HOME0 * kernel.PLANK_STEP_DEG == 360
    assert kernel.PLANKS_PER_HOME0 * kernel.PLANK_STEP_PCT == 6.0

    assert kernel.MINI_PRIM_LEFT[::-1] == "|..||.."
    assert kernel.inverse_glyphs(kernel.MINI_PRIM_LEFT[::-1]) == "|xx||xx"
    assert kernel.mini_prim() == "..||..| {-0,+0} |xx||xx"
    assert 3 * kernel.MINI_PRIM_DEG == 60
    assert 18 * kernel.MINI_PRIM_DEG == 360
    assert 18 * 2 == 36

    assert kernel.GRAVITY_PAIR[-1] == ("-1", "-1")
    assert kernel.GRAVITY_PAIR[0] == ("-0", "+0")
    assert kernel.GRAVITY_PAIR[+1] == ("+1", "+1")

    assert math.isclose(abs(kernel.PUSH_MAGNITUDE) * abs(kernel.PULL_MAGNITUDE), 1.0, rel_tol=1e-12, abs_tol=1e-12)
    assert kernel.homeo_branch(-1) == "PULL"
    assert kernel.homeo_branch(0) == "BALANCE"
    assert kernel.homeo_branch(+1) == "PUSH"
    assert kernel.homeo_force(-1) < 0
    assert kernel.homeo_force(0) == 0
    assert kernel.homeo_force(+1) > 0

    path = kernel.frozen_path()
    assert [s.layer for s in path] == [0, 1, 2]
    assert [s.occupancy for s in path] == ["0root", "carrier-open", "oe"]
    assert [s.internal_gravity_phase for s in path] == ["0G", "+G", "-G"]
    assert [s.homeo_branch for s in path] == ["BALANCE", "PUSH", "PUSH"]
    assert path[2].internal_gravity_phase == "-G"
    assert path[2].homeo_branch == "PUSH"

    xe = kernel.post_oe_xe_test()
    assert xe["status"] == "xe / POST-oe ELEMENT<->PLANK CLOCK BINDING UNBOUND"
    assert xe["clock_test"]["element_modulus"] == 10
    assert xe["clock_test"]["plank_modulus"] == 12
    assert xe["clock_test"]["gcd"] == 2
    assert xe["clock_test"]["lcm"] == 60
    assert xe["known_post_oe"]["closure_value"] == 1002
    assert xe["known_post_oe"]["ingress"] == -359.494
    assert xe["known_post_oe"]["egress"] == +359.494

    demo = kernel.demo()
    assert demo["frozen"]["status"].startswith("0e")
    assert demo["next_xe"]["status"].startswith("xe")

    return {
        "status": "0e / AE HOMEO-OE v180 TESTS PASS",
        "frozen_boundary": "L2 = oe",
        "next_xe": xe["status"],
        "tests": {
            "frozen_v92_root": "PASS",
            "phase_quantum_1_over_36": "PASS",
            "plank_30deg_0_5pct": "PASS",
            "homeo_12_plank_6pct": "PASS",
            "mini_prim_transform": "PASS",
            "mini_prim_18x20_closure": "PASS",
            "gravity_pair_ternary": "PASS",
            "push_pull_reciprocal": "PASS",
            "plank0_flip": "PASS",
            "gravity_namespace_separation": "PASS",
            "L0_L1_L2_oe_freeze": "PASS",
            "post_oe_fail_closed": "PASS",
        },
    }

if __name__ == "__main__":
    print(json.dumps(test_all(), indent=2))
