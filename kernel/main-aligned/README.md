# OASIS Main Aligned Kernel

Canonical aligned trunk as of 2026-10-07.

## Current

Current aligned version: **v32 — AZ1 scientific-civilization alignment**

Canonical monolithic source SHA-256:

`df133032c570edefeca29efa48f2e21a21f1c5edf75ae480cbc6e3c89aecefd3`

Browseable structural module:

`lean/Oasis.Fallout.AZ1Science.v32.lean`

Detailed report and manifest:

`kernel/main-aligned/v32/`

`kernel/main-aligned/CURRENT.lean.gz` is the exact gzip snapshot of v32. Use
`kernel/main-aligned/extract-current.sh` to materialize `CURRENT.lean` and verify
the source digest.

## v31 bridge

v31 formalized the corpus A→Z→A round trip as a constructed reversible traversal
rather than treating the forward corpus list itself as a literal palindrome.

## v32 fallout

AZ1 contributes a real executable state-machine package:

`deterministic research transition -> replayable chronicle -> versioned corpus -> numerical N-body fixture`

Executed results:
- uploaded `_simulate.py 200`: 9/9 PASS
- uploaded 86-entry chronicle: exact replay PASS
- corpus 859 -> 1321: 854 retained, 467 added, 5 removed
- historical `_physics.py`: STALE against current `_tick.py`
- long-horizon terminal invariant first fails at harness day 11849
- fixed-seed velocity-Verlet reference: forward/reverse returns near machine precision

The stale audit and terminal accumulator defect remain visible; they are not
silently repaired by the alignment layer.

All v32 artifacts remain HOLD-only support. They do not override Root,
durable/finality law, verified-only truth advancement, or human authority.

## Verification status

Python/state-machine/numerical tests were executed. Lean was not installed in
the alignment runtime, so the combined trunk is structurally checked but not
Lean-compiler-certified.
