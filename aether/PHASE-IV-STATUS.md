# AETHER Phase IV — Live Progress

**2 / 8 completed · 25% · AETHER-106 accepted.**

| Turn | Bound | Status | Completion |
|---|---|---|---:|
| 1 | 105 Bounded observation economy | **Accepted (synthetic)** | **12.5%** |
| 2 | 106 Sequential calibration | **Accepted (synthetic)** | **25%** |
| 3 | 107 Temporal risk budgeting | Planned | 25% |
| 4 | 108 Sparse-sensor resilience | Planned | 25% |
| 5 | 109 Recovery | Planned | 25% |
| 6 | 110 Deterministic resource scheduling | Planned | 25% |
| 7 | 111 Unseen dynamic stress | Planned | 25% |
| 8 | 112 Phase freeze | Planned | 25% |

## Turn 2 — AETHER-106

- 500 seeded cases per risk/mode: 4 true risks × IID/block10 × 4 policy comparisons.
- Four looks at 40, 140, 280, and 560 reported observations.
- Alpha spent 0.05/4 per look, one-sided binomial Clopper–Pearson bound.
- At true risk 3.5% with ten reports per independent root, naive optional sampling approved **313/500 unsafe cases**, root-aware sequential approved **0/500**.
- At IID safe risk 0.3%, root-aware sequential approved **493/500**.
- The block-aware policy also approved **0/500 safe correlated cases** because 56 independent roots did not suffice; this limitation is explicit.
- [Source, data and interactive lab](106/) committed. Pages deployment status unverified.
- **Phase IV: 25% complete. Next AETHER-107: temporal risk budgeting.**

## Turn 1 — AETHER-105

AETHER-105: 320 seeded cases, 25,600 ticks, 16,157 ACT decisions. Adaptive and fixed policies produced identical aggregate outcome counts, 2 unsafe authorized ticks each, and adaptive used 3,046,300 versus 3,584,000 observations, saving 537,700 (15.0%). Total costs: 175,185.5 adaptive versus 180,562.5 fixed (5,377 saved). **Synthetic only.**

[Experiment](105/) · [Phase IV charter](PHASE-IV-105-112.md) · [Phase III boundary closure](PHASE-III-CLOSURE.md)

`{24/[2]/[4]/(3)/(3)/(1)/(1)} · {{i}} · .dlw`
