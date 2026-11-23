# AETHER Phase VI — Measurement Integrity and Adaptive Homeostasis

**AETHER-128 local integration gate passed. PHASE VI CLOSED: 8/8 = 100% of constrained synthetic acceptance.**

| Turn | Bound | Status | Progress |
|---|---|---|---:|
| 1 | 121 Signed sensor measurement integrity | **ACCEPTED** | **12.5%** |
| 2 | 122 Calibration integrity under selective fault | **ACCEPTED** | **25%** |
| 3 | 123 Bounded recalibration and provenance | **ACCEPTED via 123B** | **37.5%** |
| 4 | 124 Noise-dependent measurement confidence | **ACCEPTED via 124B** | **50%** |
| 5 | 125 Recovery after instrument replacement | **ACCEPTED via 125B** | **62.5%** |
| 6 | 126 Adaptive calibration resource economics | **ACCEPTED** | **75%** |
| 7 | 127 Unseen sensor drift stress | **ACCEPTED via 127C** | **87.5%** |
| 8 | 128 Integration and freeze | **ACCEPTED — FROZEN** | **100%** |

## AETHER-128 — Phase VI synthesis and evidence freeze

- **200 new synthetic test episodes**, 25 seeds × eight unseen sensor response scenarios × 32 ticks = **6,400 decisions**; 1,600/1,600 repeatability, record-chain, packet-binding, probe-coverage and immutable-source gates passed in local execution.
- Frozen AETHER-127C policy **zero unsafe ACT** in this synthetic integration; **2,870 safe ACT**, **1,955 safe HOLD**, **583,050 synthetic calibration probe purchases**.
- All **12 local Phase VI experiment versions** inventoried with SHA-256 source/manifest hashes and expected PASS/FAIL status. Original failed 123, 124, 125, 127 and 127B are preserved and not counted as accepted bounds. Historical tests inventoried, not exhaustively rerun.
- Crucial limitations: same-path opaque probe ground truth, trustworthy sensor oracle and declared regularity bound remain **synthetic assumptions**; no sensor security or field measurement proof, no repeated-decision familywise risk assurance.
- **Provenance caution:** local source SHA-256 of AETHER-127C `37837c39760e972834c93386a7236de8cf2744d3f3acc8553a57a5cb21d17eee`; GitHub-authored reproduction script is **not byte-identical** to the local integration harness. Repository checkout and live Pages replay have not been independently tested.
- [AETHER-128 experiment, local-run results, hash inventory and interactive closure HTML](128/) committed.
- **Phase VI CLOSED: 8/8 = 100% of specified constrained synthetic gates.** This is a research-program accounting status, not a claim of real-world safety. Freeze prior evidence; next phase starts at 0%.

## AETHER-127C — Explicit coverage under nonlinear measurement errors

- **AETHER-127 original failure preserved**: fixed and adaptive four-probe calibration authorized **696 and 662** unsafe ACT respectively on the original holdout. Four known probes cannot certify nonlinear interpolation.
- **AETHER-127B failed**: 88 random hidden interior probes eliminated modeled unsafe actions but left coverage gaps, dropping clean safe actions **1,918 → 1,588**. No completion credit; [failed archive](127b/).
- **AETHER-127C corrected 127B** by guaranteeing a radius-1 net over **integer error-count input domain 0–100**, with randomized parity + additional concealed positions, 88 total probes/tick. Coverage is checked on every tick. Unknown domains and untrusted coverage would force HOLD.
- New 60-seed × eight-case synthetic holdout: **480 paired episodes**, 15,360 decisions/policy, **6,720/6,720** reproducibility, integrity, coverage, resource and zero-unsafe checks passed.
- Frozen adaptive policy **665 unsafe authorizations**; corrected coverage gate **0** in this synthetic model. Nonlinear blindspot (409→0) and nonlinear midrange (256→0); clean safe ACT **1,918/1,918** preserved.
- Total safe ACT **8,066 → 6,867**. Probes increased **47,640 → 1,399,320** (~29.4×); illustrative total cost increased **729,216.8 → 3,151,809.6**. This correction is **not** an economic improvement.
- **Critical model limitation:** The code uses a known synthetic sensor-response function as its ground-truth challenge oracle. Physical same-path probe secrecy, truthful reference response, response regularity across gaps, and covered operational domain are **assumptions**, not proved protections. A selective or probe-aware sensor can still defeat this; field safety is not established. GitHub checkout exact replay is not yet independently confirmed.
- [Accepted AETHER-127C executable, evidence summary and interactive laboratory](127c/) committed. Live Pages deployment unverified.
- **Turn 7 accepted within its explicitly constrained synthetic model: Phase VI 7/8 = 87.5%.** Next AETHER-128 integration and phase freeze.

## AETHER-127 — Unseen nonlinear drift, safety gate FAILED

- **480 paired synthetic episodes**, 60 untouched seeds × eight new sensor response conditions × 32 ticks; **15,360 decisions per controller**.
- Frozen AETHER-126 decision engine imported without tuning in the **local** test. 5,760/5,760 replay, SHA-256 chain, one-action, fail-closed, budget and source-freeze checks passed.
- **Safety FAILED**: adaptive **662 unsafe ACT**, fixed **696 unsafe ACT**. All from two targeted nonlinear response faults that passed all four calibration points, while underreporting true risk outcomes at other count values.
- Blind-spot case: **403 adaptive** and **421 fixed** unsafe. Midrange distortion: **259 adaptive** and **275 fixed** unsafe.
- Adaptive saved **13,800 calibration probes** (22.5%) and **41,499.2** synthetic cost units, but savings do not compensate for the failed safety gate.
- Finite pointwise calibration alone **does not certify entire sensor response curve**; both fixed and adaptive are vulnerable. Blindness is not attributable solely to reduced calibration frequency.
- **Reproducibility qualification:** The local test imports the archived local AETHER-126 source SHA-256 `9fde4f39ca3806869556561bb6f1a8654ed108f74ae53e9914ccb3631d9d4426`. Exact byte identity with GitHub's prior `126/experiment.py` has **not** been verified; independent GitHub-checkout reproduction remains necessary.
- [Failure archive, results, harness and interactive HTML](127/). Live GitHub Pages deployment remains unverified.
- **No phase credit. Phase VI remains 75%.** Next AETHER-127B: randomized *hidden* interior pilot coverage with explicit unobservable-domain HOLD, not witness/quorum or Byzantine consensus.

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
