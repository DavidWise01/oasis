# AETHER Phase X — Physical Reference Acquisition Setup and Evidence Intake

**AETHER-155 original raw-capture and timing intake PASSED. Phase X synthetic software setup readiness: 3/8 = 37.5%. Empirical physical qualification: 0% (NO PHYSICAL MEASUREMENTS). Operational authority: HOLD.**

Phase X distinguishes *software protocol development* from *actual independent reference equipment acquisition, calibration and measurements*. Passing the former cannot advance the latter. This ledger does not claim that any instrument is physically attached or any traceability certificate has been authenticated.

| Turn | Bound | Acceptance | Software setup readiness |
|---|---|---|---:|
| 1 | 153 Equipment register and commissioning contract | **ACCEPTED — synthetic only** | **12.5%** |
| 2 | 154 Independent reference identity and certificate intake | **ACCEPTED — synthetic corrected test** | **25%** |
| 3 | 155 Original physical-capture file and timing intake | **ACCEPTED — synthetic only** | **37.5%** |
| 4 | 156 Reference traceability and uncertainty budget | Planned | 37.5% |
| 5 | 157 Same-path hardware challenge procedure | Planned | 37.5% |
| 6 | 158 Physical drift/alarm acceptance thresholds | Planned | 37.5% |
| 7 | 159 Unknown-fault blind physical intake rehearsal | Planned | 37.5% |
| 8 | 160 Real-world qualification evidence decision freeze | Planned | 37.5% |

## AETHER-155 — Immutable raw-capture bytes and monotonic sample timing

- Local exact synthetic run: **25 seeds × eight conditions × 20 ticks**, **200 episodes and 4,000 decisions per policy**, **3,200/3,200** checks passed for deterministic replay, hash chaining, order, one decision, modeled safety, preserved safe cases and permanent operational HOLD.
- The signed-only comparator admitted **1,200 unsafe dry-run ACT**; the original-byte/timing gate admitted **0 unsafe**, retaining **2,800 safe dry-run ACT**, including **500/500 clean** and **500/500 legitimate clock rotation**.
- Six constructed failures: missing raw capture, appended/modified bytes, sample counter gap, clock rollback, forged timestamp origin and captured reference identity substitution. The source byte hash, challenge nonce, signed generation, counter sequence, declared sample interval and source identity must agree.
- **Physical qualification remains 0%**. The original bytes and absolute clock are synthetic, no actual instrument/timebase was observed, and all real operational permissions remain HOLD. [Blank physical-capture register](155/physical_capture_register.json) retains missing physical metadata.
- Exact locally executed Python SHA-256 `8b5a4310b2f78031ba06f8fbe148b1a05417257194bff4ea9103f3cba3831a61`. [AETHER-155 source, results, acceptance manifest and interactive lab](155/) published; GitHub source is separately authored from the local test, and independent GitHub checkout replay and live Pages status are unverified. Full locally executed audit is available in the companion ZIP.
- **Phase X setup readiness 3/8 = 37.5% synthetic; empirical qualification = 0%.** Next AETHER-156: traceability and uncertainty budget intake.

## AETHER-154 — Quarantined reference-issuer identity and calibration certificate intake

- Local corrected software test: **25 seeds × eight scenarios × 20 ticks = 200 episodes per policy, 4,000 decisions per policy**, with **3,200/3,200 deterministic gates passed**.
- Baseline signed-only comparator: **1,200 unsafe dry-run ACT**; the certificate intake gate: **0 unsafe dry-run ACT**, retaining **2,800 safe dry-run ACT** including **500/500 clean** and **500/500 valid reference rotation**.
- Tested six synthetic certificate failures: missing issuer identity, unrecognized issuer credential, serial mismatch, expired certificate, broken claimed source ancestry and altered signed uncertainty. The intake policy uses signed mock certificate plus raw record and separate mock bench; no hidden test labels passed into authorization.
- **Preserved initial failure AETHER-154A:** **400/400 hash-chain verifications failed** because the writer hashed the previous digest field but the verifier omitted it. Corrected 154 fixed the verifier's reconstruction only; the authorization gate remained unchanged. The original and corrected sources, checks, manifests and traces are in the ZIP. [Original failure record](154a/failure.json).
- **Physical qualification 0%**: the actual equipment/certificate [register](154/physical_reference_register.json) remains null. No accredited laboratory issuer, calibrated standard, physical measurement or real reference acquisition verified; all operational actions **HOLD**.
- Exact corrected local executed Python SHA-256 `c40bf52d6a1b5ed5068d6e6967d2d25130b16cee9a62963dd354f675747e9fc7`; GitHub [154](154/) includes separately authored standalone reproducer, numerical results, manifest, neon interactive HTML and uncommissioned register. Independent checkout replay and live Pages deployment remain unverified.
- **Phase X synthetic setup-readiness: 2/8 = 25%; empirical qualification: 0%.** Next AETHER-155: original physical-capture file and timing intake.

## AETHER-153 — Physical-reference acquisition setup boundary

- Exact local synthetic execution: 25 seeds × eight cases × 20 ticks = **200 paired episodes, 4,000 decisions per policy**, **3,200/3,200** deterministic acceptance checks.
- Baseline signed-only: **1,200 unsafe dry-run ACT**. The setup-gated controller: **zero unsafe dry-run ACT**, **2,800 safe dry-run ACT** retained, including **500/500 clean** and **500/500 reference rotation**.
- Six constructed faults were quarantined: missing reference serial, untrusted lab, expired calibration, missing raw capture, unverified route and challenge mismatch.
- An explicitly *uncommissioned* [equipment register](153/physical_setup_register.json) leaves serials, certificate provenance, calibration dates, actual measurement data, reference acquisition route and uncertainty blank. No hardware was connected or independently measured; **physical qualification remains 0%**. All operational ACT remain HOLD.
- Exact locally executed source SHA-256 `e61bcff26a003ae570a8279b57f45709e15fabb42cd1ad285a250db14e9a069b`; source plus 3,200 checks, seed results, traces and manifest preserved in locally generated ZIP.
- [GitHub AETHER-153 source, results, manifest, interactive HTML](153/) are committed. The GitHub Python is separately authored (not byte-identical to the local run); independent checkout replay and live Pages deployment remain unverified.

## Next AETHER-154

Define quarantined intake for actual reference instrument identity and calibration certificate credentials, retain nil values when unknown and forbid importing simulated fixture assertions as measured physical evidence.

One controller. Forward-only evidence. `{24/[2]/[4]/(3)/(3)/(1)/(1)} · {{i}} · .dlw`.
