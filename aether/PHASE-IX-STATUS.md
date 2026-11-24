# AETHER Phase IX — Real Instrument Qualification Protocol

**AETHER-146 quarantined calibration-intake synthetic gate PASSED. Software readiness: 2/8 = 25%. EMPIRICAL PHYSICAL VALIDATION: 0% (NOT PERFORMED).**

Phase IX deliberately keeps **synthetic software-protocol readiness** separate from **real physical instrument qualification**. No software result, simulated bench, mock HMAC key, acceptance counter or signature may advance the physical metric. All real-world operational permissions remain **HOLD**.

| Turn | Bound | Status | Synthetic protocol readiness |
|---|---|---|---:|
| 1 | 145 Actual-instrument qualification contract | **ACCEPTED via 145B (synthetic)** | **12.5%** |
| 2 | 146 Physical reference and certificate intake | **ACCEPTED — synthetic only** | **25%** |
| 3 | 147 Raw acquisition and provenance requirements | Planned | 25% |
| 4 | 148 Empirical uncertainty/coverage acceptance plan | Planned | 25% |
| 5 | 149 Measured same-path challenge protocol | Planned | 25% |
| 6 | 150 Drift and alarm characterization protocol | Planned | 25% |
| 7 | 151 Blind adversarial physical-data intake rehearsal | Planned | 25% |
| 8 | 152 Qualification evidence freeze | Planned | 25% |

## AETHER-146 — Quarantined reference certificate and raw-measurement intake

- Local synthetic run: **240 episodes per policy**, 30 seeds × eight certificate/acquisition cases × 20 ticks; **4,800 decisions per policy**, **3,840/3,840** deterministic checks passed.
- Signed-only comparator: **1,440 unsafe dry-run ACT**. Quarantined intake controller: **0 unsafe dry-run ACT**, retaining all **3,360 safe dry-run ACT** and **600/600** clean and valid-rotation availability.
- Faults quarantined: missing certificate, expired certificate, mismatched reference serial, altered raw SHA-256, self-issued reference standard and mismatched challenge nonce. No automatic evidence repair; fail closed on untrusted input.
- **Physical validation 0%:** The issuer root is a mock HMAC key and allowlisted string; actual accreditation, reference traceability, instrument measurements, device ingress and physical uncertainty remain unverified. Every real operational action remains HOLD.
- [Source, local results, manifest and interactive HTML](146/) committed. Published GitHub standalone script is distinct from full executed local program; checkout replay and Pages deployment are unverified.
- **Phase IX synthetic software-protocol readiness: 2/8 = 25%.** Next AETHER-147: immutable raw acquisition and provenance requirements.

## AETHER-145 — Preserved counterexample

- Original local synthetic test **FAIL**: forged reference matches an untrusted instrument claim and passes a signed-only reference consistency check.
- **240 unsafe dry-run ACT** through that circular reference path. Failure archived at [145](145/); no accepted-turn credit.
- Original source SHA-256: `7deef899c1d2c80caf24bc46bb3410825de8200a5ed572b2fed4acf9114f033d`.

## AETHER-145B — Corrected protocol-readiness acceptance

- 30 seeds × eight scenarios × 20 ticks = **240 paired episodes**, **4,800 decisions per policy**, **3,840/3,840 deterministic tests passed** on the local accepted source.
- Comparator signed-only: **1,440 unsafe dry-run ACT**. Original AETHER-145: **240 unsafe dry-run ACT**. Corrected bench-bound gate: **0 unsafe dry-run ACT**.
- Corrected contract separately signs modeled bench acquisition with its own measured value and uncertainty, and matches its nonce, tick and device generation to the instrument/reference observation. A reference merely repeating a false DUT claim fails its measurement comparison.
- **3,360 safe dry-run ACT** retained, including **600/600 clean** and **600/600 legitimate replacement**. All **operational ACT = 0**.
- **No physical instrument or independently calibrated standard was tested.** The 'independent bench' is software HMAC keyed and reads synthetic ground truth directly. Real device identity, traceability, acquisition continuity, alarm reliability and uncertainty remain unverified; physical progress **0%**.
- Local accepted Python SHA-256 `21be6c64d495f9dead48c584ba6e719eb12ec5292954cf00e148a72b0593288a`. GitHub [145B](145b/) contains a separately authored standalone demonstration, not the byte-identical full local acceptance source. GitHub-checkout execution and live Pages deployment remain unverified.
- Original full tests, CSVs, hash-chain traces and manifests are retained in the downloadable `aether145-evidence.zip` linked in the conversation.
- **Phase IX Turn 1 accepted on constrained synthetic software criteria only: 12.5% readiness, 0% empirical physical qualification.**

## Next natural bound — AETHER-146

**Physical reference and certificate intake:** define a quarantined intake protocol for real certificate metadata and raw physical measurements, reject documents lacking independent source identity, never silently substitute fixture data, and keep operational authority at HOLD until actual qualification gates pass.

One deterministic controller. Forward-only evidence. `{24/[2]/[4]/(3)/(3)/(1)/(1)} · {{i}} · .dlw`.
