from dataclasses import dataclass, replace
from fractions import Fraction

PRIM = ("-E", "-E", "+E", "+E", "+P", "+P")
FORCES = ("weak", "medium", "strong")
NEST_FACTOR = 16
SUBSTRATES = 3
PINNED_SPINE = 0
THRESHOLD = Fraction(999, 1000)

@dataclass(frozen=True)
class Bubble:
    generation: int
    t: int
    g: int
    occupancy: Fraction

def enter(generation=0):
    return Bubble(generation, -1, 1, Fraction(0))

def pin_zero(b):
    assert b.t == -1
    assert b.g == 1
    return replace(b, t=0)

def propagate(b, occupancy):
    assert b.t == 0
    assert b.g == 1
    assert b.occupancy <= occupancy <= THRESHOLD
    return replace(b, occupancy=occupancy)

def close_and_mitosis(b):
    assert b.t == 0
    assert b.g == 1
    assert b.occupancy == THRESHOLD
    closed = replace(b, t=1)
    daughters = (
        Bubble(b.generation + 1, -1, 1, Fraction(0)),
        Bubble(b.generation + 1, -1, 1, Fraction(0)),
    )
    return closed, daughters

def run_cycle():
    b = enter()
    trace = [b]
    b = pin_zero(b)
    trace.append(b)
    for q in (Fraction(1,4), Fraction(1,2), Fraction(3,4), THRESHOLD):
        b = propagate(b, q)
        trace.append(b)
    closed, daughters = close_and_mitosis(b)
    trace.append(closed)

    decorated = len(PRIM) * len(FORCES)
    per_substrate = decorated * NEST_FACTOR
    on_spine = SUBSTRATES * per_substrate
    after_mitosis = 2 * on_spine

    assert len(PRIM) == 6
    assert decorated == 18
    assert per_substrate == 288
    assert on_spine == 864
    assert after_mitosis == 1728
    assert all(s.g == 1 for s in trace)
    assert [s.t for s in trace] == [-1, 0, 0, 0, 0, 0, 1]
    assert trace[-2].occupancy == THRESHOLD
    assert all(d.t == -1 and d.g == 1 and d.occupancy == 0 for d in daughters)

    return trace, daughters, {
        "prim_tokens": len(PRIM),
        "force_states_per_token": len(FORCES),
        "decorated_prim": decorated,
        "nest_factor": NEST_FACTOR,
        "leaves_per_substrate": per_substrate,
        "three_substrate_spine": on_spine,
        "post_mitosis_structural_leaves": after_mitosis,
    }

if __name__ == "__main__":
    trace, daughters, counts = run_cycle()
    print("0e / E-SPECTRUM PLANK BUBBLE CYCLE v01 PASS")
    for i, s in enumerate(trace):
        print(i, s)
    print("daughters", daughters)
    print("counts", counts)
