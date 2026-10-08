#!/usr/bin/env python3
"""Source-level reproduction of arXiv:2610.08144 discrepancies.

Requires Python 3 and HTTPS access to raw.githubusercontent.com.
Does NOT compile Lean or prove a mathematical counterexample.
"""
from urllib.request import urlopen
import hashlib

COMMIT = "f9e8bc5"
ROOT = "https://raw.githubusercontent.com/openai/NavierStokesAndEuler/" + COMMIT + "/"
TARGETS = {
    "inverse": ("NavierStokes/SmoothFamilyTorusInverse.lean", "c607eb6f2460a3ba55dc2218072cd504bf6253bf"),
    "pressure": ("NavierStokes/R3/PressureFlux.lean", "542377decf40306a50ce2170783de99a384b8d41"),
}
def git_blob_sha(payload):
    return hashlib.sha1(b"blob " + str(len(payload)).encode() + b"\0" + payload).hexdigest()

sources = {}
for name, (path, expected) in TARGETS.items():
    with urlopen(ROOT + path, timeout=30) as response:
        raw = response.read()
    actual = git_blob_sha(raw)
    assert actual == expected, f"{name}: unexpected blob {actual} != {expected}"
    sources[name] = raw.decode("utf-8")
    print(f"PASS blob {name}: {actual}")

inverse = sources["inverse"]
pressure = sources["pressure"]
checks = [
    ("inverse declaration", "theorem norm_derivativeWord_inverse_le" in inverse),
    ("inverse first +5", "xJet (w.length + 5) (slice f p)" in inverse),
    ("inverse second +5", "xJet (w.length + 5)\n        (SmoothFourierData.swapFunction" in inverse),
    ("inverse weight power four", "(weight k ^ 4)⁻¹" in inverse),
    ("pressure declaration", "theorem exists_uniform_actual_pressure_flux_bound" in pressure),
    ("pressure dissipationRoot", "dissipationRoot (ComparisonCutoffs.cutoff R) (u - v) t / R" in pressure),
    ("pressure exponent -7/4", "R ^ (-(7 / 4 : ℝ))" in pressure),
    ("pressure inverse square", "1 / R ^ 2" in pressure),
    ("pressure cutoff power 3/4", "cutoffL6 (ComparisonCutoffs.cutoff R) (u - v) t ^ (3 / 4 : ℝ)" in pressure),
]
for label, ok in checks:
    print(("PASS" if ok else "FAIL") + " " + label)
assert all(ok for _, ok in checks), "One or more checks failed"
print("9/9 source structural checks PASS; no Lean compilation was attempted")
