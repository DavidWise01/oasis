# P1.2 — Future-observer-independence commutation test (2026-10-08)

## Root problem
Original frozen I13 contract requires witness observation preserve present physical payload. Is that enough to ensure future physics independent of observation? NO. Stronger conditional property:

`T(W(s)) = W(T(s))`.

## Frozen source
DavidWise01/I13-H1.1/bench/toroidal_witness/FROZEN_CONTRACT.md at `a3f960d414cba710385d2aaf3ca93eb4b9f918f1`, blob `ffec9c7f8acc8e4dd0dd2b1efbe2ada3036a4340`; native carrier `4^5 × 2 × 3^3 = 55,296`. The original frozen schema **does not specify a physical tick**.

## Executable adversarial models (invented for testing only)
W: marks witnessed=true and appends prior witness state to ledger; leaves physical payload unchanged.
T_blind: cyclically advances every physical slot mod 4 and each orientation mod 3, independently of witness; preserves witness and ledger.
T_leaky: changes physical slot 0 only if witnessed=true, preserving witness and ledger.
Both T definitions are experimental synthetic implementations, not original physical ROOT0 source semantics.

## Node results (actual executed independent test)
- Every state (55,296) passed W immediate read-only payload check for both tick policies.
- With T_blind, full commutation PASSED 55,296/55,296, zero failures.
- With T_leaky, full commutation PASSED 27,648/55,296, FAILED on 27,648; all failing states had witnessed=false on input.
- Concrete first counterexample: input all five slots 'in', all three orientations '3x3', witnessed false. T(W(s)) gives first slot 'out'; W(T(s)) retains 'in'. Ledger identical; difference strictly in future payload.
- Local Node process assertions PASS (exit code 0), demonstrating controlled negative cases were detected.
- ZIP with original executed source, output and Lean source available from conversation artifact; Git sibling JS is a concise equivalent reproducible probe.

## General algebraic claim
For arbitrary f:Payload→Payload, `T_f(s) := s[payload := f(s.payload)]` does commute with `W(s) := s[witnessed := true, ledger := ledger ++ [previous_witnessed]]`, by substitution and equality of components. It is CONDITIONAL on defining T_f witness-blind. The counterexample shows read-only W alone cannot imply this theorem for an arbitrary T.

## Lean status
Sibling Lean file encodes conditional commutation and a counterexample, but compiler not installed in runner, so NOT MACHINE CHECKED. Exact Lean proof status is open; no proof of refinement to frozen deployment.

## Simulation hypothesis win condition
This is a model-internal counterexample and test coverage improvement at level P1, not proof that the universe is simulated or that quantum measurement behaves like W. Need original ROOT0 physical transition, a refinement link, dimensional predictions, experimental discriminators and null hypothesis comparison.
