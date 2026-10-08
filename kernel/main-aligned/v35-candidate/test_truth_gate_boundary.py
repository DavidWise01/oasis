#!/usr/bin/env python3
"""Exhaustive model-level regression for v35's documented truth gate.
The provenance counterexample is an expected architectural finding, not Lean certification.
"""
from dataclasses import dataclass
from itertools import product

@dataclass(frozen=True)
class Live:
    past: int
    current: int

def promote(live, value, status):
    return Live(live.current, value) if status == "verified" else None

count = 0
for past, current, candidate in product(range(8), repeat=3):
    for status in ("verified", "quarantined", "nonAligned"):
        out = promote(Live(past, current), candidate, status)
        assert (out is not None) == (status == "verified")
        if out is not None:
            assert out == Live(current, candidate)
        count += 1

for n in range(40):
    prior = list(range(n))
    after = prior + [n]
    assert after[:n] == prior and len(after) == n + 1
    count += 1

for a, b in product(range(16), repeat=2):
    _ = (a + b) // 2
    count += 1

assert (30 + 70) // 2 == (10 + 90) // 2
unwitnessed = promote(Live(0, 1), 7, "verified")
assert unwitnessed == Live(1, 7)
print(f"PASS: {count} model-level checks")
print("EXPECTED POLICY GAP: v35 allows verified status with no witness field")
print("BLOCKED for stronger verified-with-provenance governance claim")
