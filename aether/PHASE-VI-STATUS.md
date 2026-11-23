# AETHER Phase VI — Measurement Integrity and Adaptive Homeostasis

**AETHER-121 accepted on synthetic acceptance gate. Phase VI: 1/8 = 12.5%.**

| Turn | Bound | Status | Progress |
|---|---|---|---:|
| 1 | 121 Signed sensor measurement integrity | **ACCEPTED** | **12.5%** |
| 2 | 122 Calibration integrity under selective fault | Planned | 12.5% |
| 3 | 123 Bounded recalibration and provenance | Planned | 12.5% |
| 4 | 124 Noise-dependent measurement confidence | Planned | 12.5% |
| 5 | 125 Recovery after instrument replacement | Planned | 12.5% |
| 6 | 126 Adaptive calibration resource economics | Planned | 12.5% |
| 7 | 127 Unseen sensor drift stress | Planned | 12.5% |
| 8 | 128 Integration and freeze | Planned | 12.5% |

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
