# ROOT0 P4.09 alignment snapshot — 2026-10-10

## Goal
A deterministic and auditable symbolic computation kernel implementing two separate emission/reception snapshots, a seven-band OSI projection, a 200-layer/200-ms logical clock with exact 10^-36 s BigInt timestamps, signed sensor/reference inputs, and guarded fail-closed state transitions. The DIATOM is a symbolic 60-point shell with z=0; the canonical four invisible-sink blockade is `{-{+{%}+}-}`. The outer layout remains `-+5 + 1`.

## Validated in this turn
Node v22.16.0: `node test_p409.mjs` locally passed 15/15 assertions in 23.84 ms on one run. Tested old signed floor replay, tampering, interrupted publication, mismatched local/external states, local rollback, restart, and coordinated history erasure weakness.

This commit set includes P405 sensor quorum, P406 diversity, P407 signed reference, P408 persistent watermark (committed previously), P409 signed external floor and its test. Paths: `docs/reality-tensor/dyson-inversions/`.

## Known gaps and explicit exit criteria
1. Missing external watermark can be treated like a new genesis by P409 when local state exists: **fail-closed behavior is not universally enforced**. Require independently authenticated genesis authorization and external floor presence before every post-genesis mutation.
2. SQLite and external trust store do not share an atomic transaction. Signed-intent protocol and crash injection are needed.
3. Both stores can be rolled back together. Need genuinely independently operated monotonic witness or hardware-rooted antirollback anchor.
4. Live sensors, real wall-clock deadlines and physical photonic/decoherence behavior are not measured by the symbolic tests.
5. Restore exact-source full integration CI on a fresh checkout; 15 local tests do not qualify as end-to-end release certification.

## Indicative progress (planning estimates, not test-derived)
- Symbolic architecture/specification: 85%.
- Local deterministic kernels & regression coverage: 75%.
- Secure publication / recovery prototype: 45%.
- Real independently deployed antirollback authority: 10%.
- Hardware/physical validation: 0%.

**Overall planning estimate:** ~55% toward a research/demo prototype; ~25% toward a production-grade, independently secured runtime. Percentages depend heavily on definition of done and are not claims of verified completeness.

Next P4.10: mandatory signed genesis + quorum-bound checkpoint, then atomic-intent recovery, process kill, and rollback adversarial tests.