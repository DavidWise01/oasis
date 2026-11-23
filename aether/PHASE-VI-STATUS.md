# AETHER Phase VI — Measurement Integrity and Adaptive Homeostasis

**AETHER-126 adaptive calibration gate passed. Phase VI: 6/8 = 75%.**

| Turn | Bound | Status | Progress |
|---|---|---|---:|
| 1 | 121 Signed sensor measurement integrity | **ACCEPTED** | **12.5%** |
| 2 | 122 Calibration integrity under selective fault | **ACCEPTED** | **25%** |
| 3 | 123 Bounded recalibration and provenance | **ACCEPTED via 123B** | **37.5%** |
| 4 | 124 Noise-dependent measurement confidence | **ACCEPTED via 124B** | **50%** |
| 5 | 125 Recovery after instrument replacement | **ACCEPTED via 125B** | **62.5%** |
| 6 | 126 Adaptive calibration resource economics | **ACCEPTED** | **75%** |
| 7 | 127 Unseen sensor drift stress | Planned | 75% |
| 8 | 128 Integration and freeze | Planned | 75% |

## AETHER-126 — Adaptive calibration resource economics

- **420 paired synthetic episodes**: 60 fresh seeds × seven environments × 32 ticks = **13,440 decisions per policy**, **5,880/5,880** deterministic checks passed.
- Fixed calibration: four interior probes for each valid packet. Adaptive: full four-probe certification at initial anchor, after device generation change, after bounded age or noisy/suspicious packet; otherwise two current monitor probes compared to a recent full calibration.
- Adaptation never replaces current signed and independently admissible risk observations. Any invalid certificate, missing counter continuity or failed full calibration yields HOLD.
- Aggregate probe purchases **50,880 fixed vs 37,080 adaptive**: **13,800 probes saved (27.12%)**. Illustrative total cost **384,873.6 fixed vs 354,104.0 adaptive**: **30,769.6 saved (7.99%)**.
- Both controllers: **0 unsafe ACT** in modeled scenarios. Safe ACT **8,322 fixed vs 8,605 adaptive** overall; stable regime **1,917/1,917** clean safe ACT, while noisy and certificate-missing cases incurred modest safe-action regressions.
- Unproven assumptions: honest HMAC issuer/protected counter, truthful bounded additive noise, affine response between full audits, **no sudden selectively hidden drift within a monitoring interval**. These synthetic results are not field safety proof; repeated pointwise confidence bounds do not give familywise guarantees.
- [AETHER-126 executable, results, manifest and interactive lab](126/) published to GitHub; live Pages status not independently verified.
- **Turn 6 accepted. Phase VI = 6/8 = 75%. Next AETHER-127: unforeseen drift and abrupt-monitor failures.**

## AETHER-125B — New instrument, new authority

- **Failed AETHER-125 retained:** 320 paired synthetic episodes; 4,480 deterministic checks all passed and guarded policy had 0 unsafe ACT, but an incorrectly defined recovery gate equated first valid calibration with first authorized risk evidence. **13 noisy-replacement cases** legitimately required HOLD even after valid calibration, so the recovery test failed (307/320), earning no completion credit. [Failed version and evidence](125/).
- **Corrected AETHER-125B:** 40 new seeded episodes × 8 scenarios × 32 inspections = **320 paired episodes** and **10,240 decisions per policy**. An independent oracle tests current *risk-admissible* observations, not merely calibration readiness.
- All **4,480/4,480** deterministic checks and all **320/320** independent risk-admissible recovery cases passed. Guarded policy 0 unsafe ACT; inherited previous-instrument authority **1,120 unsafe ACT** in the modeled attacks.
- New instrument must have its **own signed device identity, calibration generation/nonce, acquisition epoch/counter continuity, bounded noise certificate and two post-replacement fresh quality reads**. Old certificate cannot renew new authority.
- Safe ACT **8,267 inherited → 7,795 guarded**; extra HOLDs on replacement documented. Synthetic cost **664,529.6 inherited → 291,166.4 guarded** under the study's illustrative cost function.
- Assumptions: protected identity/signing authority, accurate independent synthetic probes and truthful noise bounds. A digital signature is not a scientific truth certificate; no field safety claim or multi-tick familywise risk proof.
- [Accepted AETHER-125B executable and interactive lab](125b/) committed. GitHub Pages live deployment unverified.
- **Turn 5 accepted via 125B; Phase VI 5/8 = 62.5%. Next AETHER-126: adaptive measurement economics.**

## AETHER-124B — Bounded noisy calibration intervals

- **AETHER-124 original FAILED**: using a *minimum* plausible measurement-error count to decide ACT understated risk, causing **3 unsafe authorizations** on noisy packets. Original executable, results, manifest and failed HTML remain under [124/](124/), with no completion credit.
- **AETHER-124B corrected** the sign of the uncertainty bound: four interior probes define an outer compatible affine gain/offset interval. Use **maximum** plausible risk count `(reported + noise_bound - min_offset)/min_gain` with ceil, never minimum count, before risk certification.
- **450 paired synthetic episodes**, 50 seeds × nine test regimes × 24 ticks, 10,800 decisions per policy; **6,300/6,300** deterministic checks passed.
- Corrected controller **0 unsafe ACT**, preserved **800/800** clean safe ACT. Certified-noise uncertainty ±1/±3/±6 permits **773/250/45** safe ACT; missing noise certificate forces HOLD.
- Total safe actions **6,587 point-fit → 3,259 interval-aware**; illustrative cost **242,449.6 → 362,667.2**. Availability and resource penalties explicitly recorded.
- Synthetic assumptions: trusted signed packets, genuine probe positions/ground truth, **truthful bounded additive noise**, and affine sensor model. Per-decision 95% Clopper–Pearson bound **does not control familywise error across repeated decisions**.
- [Accepted 124B executable, manifest, results and interactive lab](124b/) committed. GitHub Pages live status unverified.
- **Turn 4 accepted via 124B; Phase VI 4/8 = 50%. Next AETHER-125: bounded recovery after instrument replacement.**

## AETHER-123B — Interior probes and bounded affine recalibration

- **AETHER-123 failed acceptance**: 3-count safety margin always applied, including exact-identity calibration, reducing clean safe ACT 839→810 and shifted-hazard safe ACT 480→467. All 7,560 deterministic checks passed and zero unsafe ACT, but no completion credit. [Failed experiment and report](123/) preserved.
- **AETHER-123B corrected** identity regression: exact measured identity fit passes the original risk count unchanged; nonidentity gains/offsets receive the original +3 uncertainty margin.
- **540 paired synthetic episodes**, 60 seeded cases × 9 regimes × 24 inspections = **12,960 decisions per policy**.
- **7,560/7,560 checks** passed; **0 unsafe ACT** for both compared controllers in tested scenarios. Clean safe ACT **839/839**, hazard-shift safe ACT **480/480**.
- Four interior calibration probes **32, 96, 160, 224**. Three fit a bounded affine model (gain 0.8–1.2, |offset|≤16); fourth validates affine residual. Out-of-range, nonlinear, and saturated conditions fail closed.
- Total safe ACT rose **1,379→4,239** with bounded recalibration. Negative offset still held because of low-value clipping. Modeled calibration expense raised total cost **364,024.0→431,524.8** illustrative units.
- Trusted same-path opaque probes, calibration truth, HMAC signing and affine relevance are synthetic assumptions, not real-world assurance.
- [Accepted corrected experiment, results and interactive lab](123b/) verified in GitHub; Pages deployment not independently checked.
- **Turn 3 accepted via 123B. Phase VI 3/8=37.5%. Next AETHER-124: noise-dependent calibration uncertainty.**

## AETHER-122 — Opaque same-path pilot calibration

- **420 paired synthetic episodes**: 60 fresh seeds × seven sensor-fault regimes × 24 inspections, **10,080 decisions/controller**.
- Publicly announced challenges can be answered correctly while ordinary signed risk observations are selectively biased; public-only gate issued **1,544 unsafe ACT**.
- Opaque same-path digital pilot checks (known 0/128 expected errors) refused every modeled unsafe ACT: **0 unsafe** with **5,040/5,040** deterministic checks passed.
- Clean safe ACT **840/840** and risk-transition safe ACT **660/660** preserved. Across all regimes, safe ACT fell **4,860 → 2,580**, reflecting an availability penalty in faulty measurement conditions.
- Simulated illustrative cost: public-only **919,520.0** versus opaque-pilot **279,148.8** units. Results are modeling-specific.
- **Critical assumption:** pilot concealment and identical ordinary-channel handling until a signed output commitment. A sensor that can identify/falsify pilots or selectively target inputs bypasses the gate. Not a proof against malicious science.
- Saturated upper-value pilot fails to flag positive bias, a preserved limitation for the next phase bound.
- [AETHER-122 source, report, results and interactive lab](122/) committed; live Pages status remains unverified.
- **Turn 2 accepted: Phase VI 2/8 = 25%. Next AETHER-123: bounded calibration integrity under non-saturating inputs.**

## AETHER-121 — Calibration challenge integrity

- 60 unseen seeds × eight synthetic sensor conditions × 24 inspections = **480 paired episodes**; **11,520 decisions per policy**.
- Both risk observations and low/high known challenges share the same simulated sensor path. Authenticated packets are **not automatically accurate**.
- Signed-only comparator **1,118 unsafe authorizations** versus calibrated controller **0** in the simulated faults.
- **840/840** legitimate clean safe ACT preserved; **539/539** safe ACT preserved in the shifted-risk condition.
- Across all scenarios, safe actions fell from **5,578** to **2,938** because the calibrated controller rejects suspect sensors. This is a real availability limitation.
- **5,760/5,760** deterministic replay, hash chain, signature, current-packet, fail-closed calibration and zero-unsafe checks passed.
- Synthetic cost with per-tick calibration charge: **760,950.4** (signed-only) vs **418,678.4** (calibrated) illustrative units; not a field prediction.
- Trusted challenge source, challenge scheduling, HMAC key and sensor equal-treatment are assumptions. Selective misreporting during non-challenge observations can evade this test. No witness/quorum machinery.
- [AETHER-121 executable, results and interactive laboratory](121/). GitHub Pages deployment live status unverified.
- **Phase V remains frozen at 100%. Phase VI earns turn 1 only.**

## Operating invariant

**One deterministic controller. Forward-only observations. Evidence validity ≠ measurement correctness. Preserve every failed experiment without overwriting its ancestry.**

`{24/[2]/[4]/(3)/(3)/(1)/(1)} · {{i}} · .dlw`
