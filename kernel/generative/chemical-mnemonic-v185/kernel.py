#!/usr/bin/env python3
"""Chemical Mnemonic v185 — discrete recoverability/time-ring model.

Model boundary:
- "mnemonic" means a chemically persistent/recoverable trace inside a declared
  observation window.
- This is an abstract finite-state model, not a universal chemical decay law.
- Real kinetics require compound, environment, assay, temperature, water, etc.

States monotonically lose recoverability under decomposition:
STRONG -> MEDIUM -> WEAK -> ZERO
ZERO is absorbing.

Father-Time rings index elapsed decomposition stages.
Mother-Nature disposition is an observation label:
reuse / hold / release.
"""
from dataclasses import dataclass
from enum import IntEnum
from typing import Iterable

class Strength(IntEnum):
    ZERO = 0
    WEAK = 1
    MEDIUM = 2
    STRONG = 3

class Disposition(IntEnum):
    RELEASE = 0
    HOLD = 1
    REUSE = 2

@dataclass(frozen=True)
class Ring:
    stage: int
    start: float
    end: float

@dataclass(frozen=True)
class Trace:
    strength: Strength
    ring: Ring
    disposition: Disposition

def degrade(s: Strength, hits: int = 1) -> Strength:
    if hits < 0:
        raise ValueError("hits must be >= 0")
    return Strength(max(0, int(s) - hits))

def recoverable(s: Strength) -> bool:
    return s != Strength.ZERO

def disposition(s: Strength) -> Disposition:
    if s >= Strength.MEDIUM:
        return Disposition.REUSE
    if s == Strength.WEAK:
        return Disposition.HOLD
    return Disposition.RELEASE

def father_time_rings(boundaries: Iterable[float]) -> list[Ring]:
    xs = list(boundaries)
    if len(xs) < 2:
        raise ValueError("need at least two time boundaries")
    if any(b < a for a, b in zip(xs, xs[1:])):
        raise ValueError("boundaries must be monotone")
    return [Ring(i, xs[i], xs[i+1]) for i in range(len(xs)-1)]

def walk(initial: Strength, rings: list[Ring]) -> list[Trace]:
    s = initial
    out = []
    for r in rings:
        out.append(Trace(s, r, disposition(s)))
        s = degrade(s)
    return out

def lineage_tether(parent: Strength, generations: int) -> Strength:
    return degrade(parent, generations)

def decomposition_tether(source: Strength, stages: int) -> Strength:
    return degrade(source, stages)

def validate() -> None:
    assert degrade(Strength.STRONG) == Strength.MEDIUM
    assert degrade(Strength.MEDIUM) == Strength.WEAK
    assert degrade(Strength.WEAK) == Strength.ZERO
    assert degrade(Strength.ZERO) == Strength.ZERO

    cases = 0
    for s in Strength:
        prev = s
        for n in range(1001):
            cur = degrade(s, n)
            assert cur <= prev
            assert cur <= s
            if prev == Strength.ZERO:
                assert cur == Strength.ZERO
            prev = cur
            cases += 1

    assert disposition(Strength.STRONG) == Disposition.REUSE
    assert disposition(Strength.MEDIUM) == Disposition.REUSE
    assert disposition(Strength.WEAK) == Disposition.HOLD
    assert disposition(Strength.ZERO) == Disposition.RELEASE

    rings = father_time_rings([0, 1, 2, 5, 10])
    assert len(rings) == 4
    assert [(r.start, r.end) for r in rings] == [(0,1),(1,2),(2,5),(5,10)]

    seq = [t.strength for t in walk(Strength.STRONG, father_time_rings(range(0, 7)))]
    assert seq == [
        Strength.STRONG, Strength.MEDIUM, Strength.WEAK,
        Strength.ZERO, Strength.ZERO, Strength.ZERO
    ]

    for s in Strength:
        for n in range(32):
            assert lineage_tether(s, n) == decomposition_tether(s, n)

    print({
        "status": "PASS",
        "exhaustive_monotonic_cases": cases,
        "strength_states": len(Strength),
        "zero_absorbing": True,
        "ring_sequence": [x.name for x in seq],
        "seal": "0e / CHEMICAL MNEMONIC v185 EXECUTABLE PASS",
    })

if __name__ == "__main__":
    validate()
