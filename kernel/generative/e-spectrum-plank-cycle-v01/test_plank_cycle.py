from plank_cycle import run_cycle, THRESHOLD

trace, daughters, counts = run_cycle()

assert trace[0].t == -1
assert trace[1].t == 0
assert trace[-1].t == 1
assert trace[-2].occupancy == THRESHOLD
assert all(s.g == 1 for s in trace)

assert len(daughters) == 2
assert daughters[0].generation == 1
assert daughters[1].generation == 1

assert counts["prim_tokens"] == 6
assert counts["decorated_prim"] == 18
assert counts["leaves_per_substrate"] == 288
assert counts["three_substrate_spine"] == 864
assert counts["post_mitosis_structural_leaves"] == 1728

print("0e / E-SPECTRUM PLANK BUBBLE TEST PASS")
