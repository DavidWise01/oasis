# AETHER Phase VIII — Physical Validation Readiness and Empirical Evidence

**AETHER-144 local integration PASS. PHASE VIII FROZEN: 8/8 = 100% of synthetic software readiness. PHYSICAL VALIDATION: 0% (NOT PERFORMED).**

Phase VIII deliberately has two non-interchangeable progress measures. The phase percentage tracks completed **software/readiness acceptance turns**. The physical-evidence percentage tracks actual observed and independently validated instrument measurements. It remains **0%** until real evidence exists.

| Turn | Bound | Acceptance | Synthetic-readiness progress |
|---|---|---|---:|
| 1 | 137 Independent physical validation readiness | **ACCEPTED — synthetic only** | **12.5%** |
| 2 | 138 Instrument identity and acquisition receipt contract | **ACCEPTED — synthetic only** | **25%** |
| 3 | 139 Independent calibration reference evidence | **ACCEPTED — synthetic only** | **37.5%** |
| 4 | 140 Physical uncertainty and coverage requirements | **ACCEPTED — synthetic only** | **50%** |
| 5 | 141 Empirical same-path insertion readiness | **ACCEPTED — synthetic only** | **62.5%** |
| 6 | 142 Measured drift and alarm requirements | **ACCEPTED — synthetic only** | **75%** |
| 7 | 143 Adversarial hardware-readiness failure modes | **ACCEPTED — synthetic only** | **87.5%** |
| 8 | 144 Integrated readiness evidence freeze | **ACCEPTED — SYNTHETIC FREEZE** | **100%** |

## AETHER-144 — Phase VIII synthetic readiness integration and empirical-gap freeze

- **200 fresh-seed synthetic episodes**, 25 seeds × eight sensor-reference scenarios × 24 ticks, **4,800 controller decisions**, **1,600/1,600** deterministic replay, SHA-256 trace, ordered action, source freeze, reference gate and no-real-ACT checks passed in local test.
- Frozen local AETHER-143 controller: **zero unsafe dry-run ACT**, **3,600 safe dry-run ACT**, **zero operational ACT**. Clean and legitimate rotation cases each preserve **600/600 safe dry-run ACT**.
- All **seven previous local Phase VIII archives** (137–143) were inventoried, with source and manifest SHA-256 hashes. Their original archives were preserved and older tests were not exhaustively rerun.
- **Physical validation 0%**: the 'external bench' is a synthetic ground-truth oracle, signing roots are mock keys, and no independent physical calibration, actual ingress path continuity, measured drift/alarms, uncertainty coverage or real reference data was validated. **Operational authority remains HOLD**.
- Source reproducibility: published GitHub `aether/144/experiment.py` is a separately authored checkout harness that imports the GitHub version of AETHER-143; local accepted experiment imports frozen local AETHER-143. Exact numerical checkout replay has **not been independently verified**.
- [AETHER-144 integration results, manifest, local SHA-256 inventory, runnable checkout script and interactive HTML](144/) committed; live Pages deployment not verified.
- **Phase VIII CLOSED at 8/8=100% of synthetic software-readiness tests. Independent physical validation is distinct and remains 0%.** The next phase should establish a real-world qualification test protocol from a zero empirical baseline, not create another paper guarantee.

## AETHER-143 — Adversarial reference-root compromises and unattested physical truth

- Local **320 paired synthetic episodes**, 40 seeds × eight conditions × 24 ticks = **7,680 decisions per policy**, **5,120/5,120** replay, hash chain, chronological, one-action, safety, fail-closed, clean availability and physical HOLD checks passed.
- Signed-only comparator authorized **1,920 unsafe dry-run ACT** in six constructed adversarial regimes (compromised reference root, replayed attestation, tampered calibration, false same-path assertion, suppressed alarm and dual digital compromise). Bench-gated model authorized **zero unsafe dry-run ACT**. **5,760 safe dry-run ACT** were preserved, including clean and valid rotation **960/960** each.
- This is **not a demonstration that software can defeat an actually compromised physical reference**. The simulation includes an independently signed 'bench' reading which directly receives synthetic physical ground truth. A dishonest actual bench or shared compromise ancestry is beyond the proof. Real-world operational actions **remain HOLD** and empirical physical validation is **0%**.
- Local executed Python SHA-256 `8a629056bcb9fdd67a01939788e62fa42cf90e997dc1b3f3f324608912c3d547`. GitHub reproducer is authored separately; exact checkout replay unverified.
- [AETHER-143 reproducibility script, result summary, assumptions and interactive HTML](143/) committed; live Pages deployment unverified.
- **Synthetic readiness advances to 7/8 = 87.5%**. Next AETHER-144: readiness integration freeze, while physical validation stays separate.

## AETHER-142 — Bounded drift and alarm requirements

- Local modeled experiment: **320 episodes per policy** (40 seeds × eight instrument/alarm conditions × 24 ticks), **7,680 decisions per policy** and **5,120/5,120** deterministic replay, hash-chain, monotonic-time, fail-closed, no-unsafe and availability checks passed.
- Signed-only comparator authorized **1,600 unsafe dry-run ACT** across concealed sensor jump, missed alarm, understated drift, stale readout, and forged software alarm conditions. The simulated external-reference and drift gate authorized **zero unsafe dry-run ACT**, preserving **6,080 safe dry-run ACT** including **960/960** each in clean, valid rotation, and bounded slow drift.
- The gated path requires protected model source identity, generation, nonce, acquisition tick/path, fresh reference value, bounded reference divergence, declared uncertainty, and drift-rate constraint. All real operational actions remain HOLD.
- **Important:** The independently trusted reference, measurement truth, path receipt and alarm are **test-fixture assumptions**. No actual drift rates, reference readings or alarm detection rates were measured. Synthetic no-unsafe result is not a physical guarantee.
- Tested local source SHA-256 `77bfcbd0b8a803654df92e487cb127b58a2708a24f25af6aa6640552cc68c2d7`. GitHub `aether/142/experiment.py` is a separately authored corresponding implementation: byte identity and checkout replay are unverified.
- [AETHER-142 complete 5,120-row acceptance CSV, results, seed data, trace samples, Python and interactive Pages laboratory](142/) committed. Live Pages deployment unverified.
- **Phase VIII software readiness 6/8 = 75%; empirical physical validation remains 0%.** Next AETHER-143: adversarial physical-attestation failure readiness.

## AETHER-141 — Same-path calibration insertion and operational ingress binding

- **Local synthetic PASS:** 40 seeds × eight acquisition scenarios × 24 ticks = **320 paired episodes**, **7,680 decisions per policy**; all **5,120/5,120** deterministic replay, hash-chain, single-action, ordering, zero-unsafe, bound-receipt, clean/rotation availability and operational-HOLD checks passed.
- Signed-only comparator authorized **1,920 unsafe dry-run ACT** across split-path, probe-bypass, replayed acquisition receipt, substituted issuer, swapped session and latency anomalies. The protected-receipt model authorized **0 unsafe dry-run ACT** while retaining **5,760 safe dry-run ACT**, including **960/960 clean** and **960/960 valid rotation**.
- In the model the ingress receipt binds instrument identity, generation, fresh nonce/counter, calibration session, probe and measurement route, timing and protected acquisition-issuer root.
- **Physical evidence 0%:** The supposed independent ingress issuer is a mock HMAC key and physical route truth comes from the test generator. There is **no real protected acquisition trace or independent reference measurement**. No operational ACT was authorized.
- Local executed source SHA-256 `f851e4a1cea68e3def327ce52e55420c06f7ff705ffe9dc442407ab6ac1c70b0`. The published GitHub `141/experiment.py` is a separately authored checkout reproducer and numerical replay is not independently verified.
- [AETHER-141 source, local result summary, manifest, report and interactive lab](141/) committed. Live Pages verification outstanding.
- **Phase VIII: 5/8 = 62.5% software-readiness acceptance; empirical physical validation 0%.** Next bound AETHER-142: measured drift and alarm requirements.

## AETHER-140 — Physical uncertainty budget and coverage claim boundary

- Local synthetic run: **320 paired cases**, 40 seeds × eight conditions × 24 ticks, **7,680 decisions per policy**, **5,120/5,120 deterministic checks passed**. All six model acceptance gates passed.
- Signed-only comparator authorized **1,920 unsafe dry-run ACT** in constructed uncertainty failures. The model-budget gate authorized **0 unsafe dry-run ACT** and preserved **5,760 safe ACT**, including **960/960 clean** and **960/960 valid calibration rotation**. **All operational ACT remain HOLD**.
- Rejected missing budget, unsupported statistical-coverage claims, shared calibration ancestry incorrectly treated as independent, upper risk crossing the action threshold, expired uncertainty records and negative/underreported budgets.
- Illustrated conservative synthetic upper risk equals mock reference value + 0.001 random + 0.001 reference + 0.002 shared + 0.003 systematic. This worst-case sum is an asserted model envelope; **no measured coverage rate or calibrated confidence interval exists**.
- **Physical validation 0%:** No actual reference data, metrological qualification, calibration samples or real-world hardware measurements. The asserted traceability root and budget are synthetic strings/constants. HOLD on all operational decisions.
- Local executed Python SHA-256 `9e2e5260c2f7fe62405b14f2fd617a4e9cf9e171387352e36e8475efd2959dcf`. GitHub `140/experiment.py` is separately authored and no independent GitHub-checkout replay has been verified.
- [AETHER-140 experiment and interactive HTML evidence](140/) committed; live Pages status unverified.
- **Phase VIII readiness: 4/8 = 50%; physical assurance: 0%.** Next AETHER-141: same-path empirical insertion readiness.

## AETHER-139 — Reference-standard source ancestry and acquisition-bound values

- Local **320 paired synthetic cases**, 40 seeds × eight reference-chain conditions × 24 ticks = **7,680 decisions per policy**, **5,120/5,120 deterministic gates passed**.
- The signed-transport comparator permitted **1,920 unsafe dry-run ACT** in constructed reference-lineage failures. A reference-evidence-contract controller permitted **0 unsafe dry-run ACT** and preserved **5,760 safe dry-run ACT**, including **960/960** clean and **960/960** valid certificate rotation.
- Controller rejects shared-root calibration, counterfeit signing roots, expired reference certificates, swapped reference identity, invalid uncertainty budgets and acquisition measurements missing the signed nonce/tick/path link.
- **Empirical qualification remains 0%:** The reference root is a software HMAC key, the so-called national traceability origin is a simulated certificate string, and reference values are produced from ground truth in a test fixture. No independent physical standard or measured source lineage was validated. Every operational action remains **HOLD**.
- Repo source `139/experiment.py` is independently authored from executed `experiment_local.py`; byte-identical checkout replay is **unverified**. [Experiment source, local-run summary, contract report and interactive laboratory](139/) are committed, but live GitHub Pages status is unverified.
- **Phase VIII synthetic readiness: 3/8 = 37.5%. Physical progress 0%.** Next natural bound AETHER-140: traceable uncertainty and empirical coverage contract.

## AETHER-138 — Model-bound protected acquisition receipts, physical permissions still HOLD

- **320 paired synthetic episodes**, eight acquisition states × 40 seeds × 24 ticks, **7,680 decisions per policy**; local execution passed **5,120/5,120 deterministic integrity, replay, temporal-binding, protected-receipt, fail-closed and clean-availability checks**.
- Signed-only transport authentication falsely allowed **1,920 unsafe ACT** under cloned software keys, stale references, replayed acquisition counters, replaced ingress paths, forged hardware claims, and missing receipts; modeled bound-receipt gate allowed **zero unsafe ACT**.
- Clean and valid device-rotation scenarios each preserved **960/960 safe dry-run ACT**; **5,760 safe dry-run ACT** overall across all scenarios. All **7,680 physical operational ticks remained HOLD**, because no genuine hardware attestation exists.
- The receipt contract binds instrument identity, generation, counter/tick, challenge nonce, acquisition path, independently issued reference identity/root, reference epoch/expiry, uncertainty and readout before accepting a **synthetic** authorization.
- **Critical limitation:** The supposed protected hardware issuer is an HMAC key in a software fixture, and reference risk is generated from scenario ground truth. These signatures are **not genuine hardware attestation**, they cannot validate a physically shared acquisition path, and no real laboratory or instrument was connected. **Physical evidence validated = 0%.**
- Local executed source SHA-256 `ba26f9ab3554bba44d197a9aacbc16e5c329b41c6f41544cd4a3193696c140dd`. The published GitHub checkout reproducer is **separately authored** and byte identity / independent numerical replay have **not** been verified.
- [AETHER-138 Python reproduction script, evidence summary, assumptions and interactive Pages](138/) committed. Live Pages status unverified.
- **Turn 2 accepted on constrained synthetic readiness only: Phase VIII 2/8 = 25%.** Next AETHER-139: external calibration-reference evidence and document authenticity.

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
