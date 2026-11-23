# AETHER Phase VIII — Physical Validation Readiness and Empirical Evidence

**AETHER-137 bounded synthetic software readiness PASS: Phase VIII 1/8 = 12.5%. PHYSICAL VALIDATION: 0% (NOT PERFORMED).**

Phase VIII deliberately has two non-interchangeable progress measures. The phase percentage tracks completed **software/readiness acceptance turns**. The physical-evidence percentage tracks actual observed and independently validated instrument measurements. It remains **0%** until real evidence exists.

| Turn | Bound | Acceptance | Synthetic-readiness progress |
|---|---|---|---:|
| 1 | 137 Independent physical validation readiness | **ACCEPTED — synthetic only** | **12.5%** |
| 2 | 138 Instrument identity and acquisition receipt contract | Planned | 12.5% |
| 3 | 139 Independent calibration reference evidence | Planned | 12.5% |
| 4 | 140 Physical uncertainty and coverage requirements | Planned | 12.5% |
| 5 | 141 Empirical same-path insertion readiness | Planned | 12.5% |
| 6 | 142 Measured drift and alarm requirements | Planned | 12.5% |
| 7 | 143 Adversarial hardware-readiness failure modes | Planned | 12.5% |
| 8 | 144 Integrated readiness evidence freeze | Planned | 12.5% |

## AETHER-137 — Physical evidence cannot be manufactured by synthetic signing

- Local **400 seeded synthetic episodes per policy**, eight test conditions × 50 seeds × 24 ticks = **9,600 decisions per policy**. Three policies compared: signature-only, synthetic readiness dry-run, and the real-world physical action gate.
- **8,400/8,400** deterministic replay, hash chain, single action, ordered counter and fail-closed checks passed.
- Signature-only comparator falsely authorized **3,500 unsafe ACT** in constructed cases. Synthetic readiness dry-run **0 unsafe ACT**, preserving clean **1,200/1,200 safe ACT**.
- **Physical gate: 0 ACT of any kind**, for the entire test. This is correct HOLD behavior because **no real instrument, independently validated reference standard, hardware attestation or empirical calibration result exists in the input**. A no-ACT policy cannot establish safe operating availability.
- Synthetic failures: expired calibration, absent traceability, different calibration device, swapped acquisition route, excess measurement uncertainty, replayed acquisition counter, and self-proclaimed 'physical' receipt. None can confer permission via a fixture signature.
- **Physical evidence requirements:** identified real hardware, traceable calibration standard and validity period, uncertainty budget, independent reference, observed same acquisition path, continuous current counters and a trusted external attestation channel. Software must not equate a fixture field with physical validation.
- Local executed source SHA-256 `291e3e0aa1b29cf45d78828106a105b7434fa402876a0b2a9fa65404bad32a3d`. The GitHub checkout reproducer is independently authored; independent reproduction remains unverified.
- [AETHER-137 source, local evidence and interactive HTML](137/) committed; GitHub Pages live deployment unverified.
- **Turn 1 accepted on synthetic readiness terms. Phase VIII = 12.5% of software/readiness milestones, but physical empirical validation = 0%.** Phase VII remains frozen at 100% of its separately declared synthetic program.

## Boundaries

One controller; forward-only evidence; fail-closed physical action. No witness quorum, consensus vote, or Byzantine machinery. Unknown physical provenance → HOLD. A signature proves only its bytes and signer, not physical accuracy.

`{24/[2]/[4]/(3)/(3)/(1)/(1)} · {{i}} · .dlw`
