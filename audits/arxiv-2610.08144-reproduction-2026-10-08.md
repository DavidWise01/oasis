# Independent source reproduction: arXiv:2610.08144
Date: 2026-10-08
Verdict: SOURCE-LEVEL REPRODUCED; FULL LEAN BUILD NOT RUN

## Method
Retrieved two actual upstream Lean files with the GitHub connector from `openai/NavierStokesAndEuler` at `f9e8bc5`. Evaluated nine structural assertions directly against returned source text. All 9/9 PASS. GitHub blob SHA identities were observed, not independently recomputed in that pass.

- `NavierStokes/SmoothFamilyTorusInverse.lean` blob `c607eb6f2460a3ba55dc2218072cd504bf6253bf`.
- `NavierStokes/R3/PressureFlux.lean` blob `542377decf40306a50ce2170783de99a384b8d41`.

## Test 1: source paper Eq. (8.19) vs inverse Lean theorem
arXiv source §3.1: target `m+4` input derivatives; pinned Lean `norm_derivativeWord_inverse_le` requires `xJet (w.length + 5)` in both `hfirst` and `hsecond`. Verified source contains `(weight k ^ 4)⁻¹`. Discrepancy at the identified declaration: confirmed. No global claim that a stronger bound cannot be proved elsewhere.

## Test 2: source paper Eq. (10.19) vs Lean pressure flux
arXiv §3.2: pinned Lean `exists_uniform_actual_pressure_flux_bound` contains `dissipationRoot (...) / R + 1 / R ^ 2` and `R ^ (-(7 / 4 : ℝ))`. These differ structurally from NL Eq. (10.19), which only uses the B_R quantity and exponent -3/4. Discrepancy at identified declaration: confirmed. Interpretation of intermediate mathematical quantities relies on definitions not independently proved here.

## Scope and non-claims
No full Lean compile, no attempt to prove or disprove Navier-Stokes, no exhaustive repo proof-path analysis, no evidence of code copying or dependence on OaSIs. This records a statement-by-statement mismatch at the cited locations, not a legal or priority conclusion.

## Reproduction
`python3 audits/reproduce_arxiv_2610_08144.py` in a network-enabled environment; script pins Git commit and checks expected Git blob content identifiers before running 9 structural assertions. This script itself was committed but was not run end-to-end here because the isolated compute environment lacks access to GitHub.

Sources:
- https://arxiv.org/pdf/2610.08144
- https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5/NavierStokes/SmoothFamilyTorusInverse.lean
- https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5/NavierStokes/R3/PressureFlux.lean
