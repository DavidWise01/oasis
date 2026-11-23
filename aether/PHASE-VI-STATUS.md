# AETHER Phase VI — Measurement Integrity and Adaptive Homeostasis

**AETHER-123B corrected acceptance gate passed. Phase VI: 3/8 = 37.5%.**

| Turn | Bound | Status | Progress |
|---|---|---|---:|
| 1 | 121 Signed sensor measurement integrity | **ACCEPTED** | **12.5%** |
| 2 | 122 Calibration integrity under selective fault | **ACCEPTED** | **25%** |
| 3 | 123 Bounded recalibration and provenance | **ACCEPTED via 123B** | **37.5%** |
| 4 | 124 Noise-dependent measurement confidence | Planned | 37.5% |
| 5 | 125 Recovery after instrument replacement | Planned | 37.5% |
| 6 | 126 Adaptive calibration resource economics | Planned | 37.5% |
| 7 | 127 Unseen sensor drift stress | Planned | 37.5% |
| 8 | 128 Integration and freeze | Planned | 37.5% |

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
