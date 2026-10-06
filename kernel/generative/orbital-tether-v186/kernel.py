#!/usr/bin/env python3
"""OaSIs Orbital Tether v186

Five-phase orbital clock + standard two-body invariant benchmark.

Physics layer:
  specific orbital energy  eps = |v|^2/2 - mu/r
  specific angular momentum h = r x v
  bound/parabolic/unbound classification by the sign of eps

Model layer:
  Father-Time ring = exact phase in {0,1/5,2/5,3/5,4/5}
  closure at 5/5 wraps to 0 and increments revolution count

The five-phase clock is a discrete observation/control layer laid over orbital
mechanics. It is not a claim that physical orbits move in five jumps.
"""
from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction
from math import cos, sin, sqrt, pi
from typing import Iterable

PHASE_DEN = 5

@dataclass(frozen=True)
class PhaseClock:
    phase: int = 0
    revolutions: int = 0

    def __post_init__(self):
        if not (0 <= self.phase < PHASE_DEN):
            raise ValueError("phase must be 0..4")
        if self.revolutions < 0:
            raise ValueError("revolutions must be >= 0")

    @property
    def fraction(self) -> Fraction:
        return Fraction(self.phase, PHASE_DEN)

    def step(self) -> "PhaseClock":
        if self.phase == PHASE_DEN - 1:
            return PhaseClock(0, self.revolutions + 1)
        return PhaseClock(self.phase + 1, self.revolutions)


def advance(clock: PhaseClock, n: int) -> PhaseClock:
    if n < 0:
        raise ValueError("n must be >= 0")
    out = clock
    for _ in range(n):
        out = out.step()
    return out


def specific_energy(mu: float, r: tuple[float, float], v: tuple[float, float]) -> float:
    rr = sqrt(r[0] * r[0] + r[1] * r[1])
    vv2 = v[0] * v[0] + v[1] * v[1]
    return 0.5 * vv2 - mu / rr


def specific_h(r: tuple[float, float], v: tuple[float, float]) -> float:
    return r[0] * v[1] - r[1] * v[0]


def energy_class(eps: float, tol: float = 1e-12) -> str:
    if eps < -tol:
        return "BOUND"
    if eps > tol:
        return "UNBOUND"
    return "PARABOLIC"


def solve_kepler(M: float, e: float) -> float:
    """Solve E - e sin E = M for 0 <= e < 1 by Newton iteration."""
    if not (0 <= e < 1):
        raise ValueError("elliptic benchmark requires 0 <= e < 1")
    E = M
    for _ in range(30):
        f = E - e * sin(E) - M
        fp = 1 - e * cos(E)
        d = f / fp
        E -= d
        if abs(d) < 1e-15:
            break
    return E


def ellipse_state(mu: float, a: float, e: float, mean_fraction: float):
    """Analytic planar elliptic state at a fraction of one orbital period."""
    M = 2 * pi * mean_fraction
    E = solve_kepler(M, e)
    cE, sE = cos(E), sin(E)
    fac = sqrt(1 - e * e)
    x = a * (cE - e)
    y = a * fac * sE
    rr = a * (1 - e * cE)
    speed_fac = sqrt(mu * a) / rr
    vx = -speed_fac * sE
    vy = speed_fac * fac * cE
    return (x, y), (vx, vy)


def benchmark_ellipse(mu: float, a: float, e: float, samples: int = 2001):
    expected_eps = -mu / (2 * a)
    expected_h = sqrt(mu * a * (1 - e * e))
    max_eps_err = 0.0
    max_h_err = 0.0
    for i in range(samples):
        f = i / (samples - 1)
        r, v = ellipse_state(mu, a, e, f)
        max_eps_err = max(max_eps_err, abs(specific_energy(mu, r, v) - expected_eps))
        max_h_err = max(max_h_err, abs(specific_h(r, v) - expected_h))
    return {
        "a": a,
        "e": e,
        "samples": samples,
        "expected_energy": expected_eps,
        "expected_h": expected_h,
        "max_energy_abs_error": max_eps_err,
        "max_h_abs_error": max_h_err,
    }


def validate() -> None:
    # Exact five-phase closure / ring clock.
    c0 = PhaseClock()
    seq = [c0.fraction]
    c = c0
    for _ in range(5):
        c = c.step()
        seq.append(c.fraction)
    assert seq == [
        Fraction(0, 5), Fraction(1, 5), Fraction(2, 5),
        Fraction(3, 5), Fraction(4, 5), Fraction(0, 5)
    ]
    assert c == PhaseClock(0, 1)

    # Exhaustive modular clock benchmark.
    clock_cases = 0
    for p in range(5):
        for rev in range(17):
            start = PhaseClock(p, rev)
            end = advance(start, 5)
            assert end.phase == p
            assert end.revolutions == rev + 1
            for n in range(101):
                got = advance(start, n)
                total = p + n
                assert got.phase == total % 5
                assert got.revolutions == rev + total // 5
                clock_cases += 1

    # Standard orbital energy sign classification at r=1, mu=1.
    assert energy_class(specific_energy(1.0, (1.0, 0.0), (0.0, 1.0))) == "BOUND"
    assert energy_class(specific_energy(1.0, (1.0, 0.0), (0.0, sqrt(2.0))), 1e-10) == "PARABOLIC"
    assert energy_class(specific_energy(1.0, (1.0, 0.0), (0.0, 1.5))) == "UNBOUND"

    # Analytic invariant sweeps. These test formulas independently across the orbit.
    circular = benchmark_ellipse(1.0, 1.0, 0.0)
    ellipse = benchmark_ellipse(1.0, 1.7, 0.55)
    for row in (circular, ellipse):
        assert row["max_energy_abs_error"] < 2e-12
        assert row["max_h_abs_error"] < 2e-12

    # Five observation phases on an eccentric ellipse preserve invariants.
    phase_rows = []
    for k in range(5):
        f = k / 5
        r, v = ellipse_state(1.0, 1.7, 0.55, f)
        phase_rows.append((k, specific_energy(1.0, r, v), specific_h(r, v)))
    e0, h0 = phase_rows[0][1], phase_rows[0][2]
    assert all(abs(eps - e0) < 2e-12 and abs(h - h0) < 2e-12 for _, eps, h in phase_rows)

    print({
        "status": "PASS",
        "clock_cases": clock_cases,
        "phase_sequence": [str(x) for x in seq],
        "circular": circular,
        "ellipse": ellipse,
        "five_phase_invariants": phase_rows,
        "seal": "0e / OASIS ORBITAL TETHER v186 EXECUTABLE PASS",
    })


if __name__ == "__main__":
    validate()
