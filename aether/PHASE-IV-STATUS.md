# AETHER Phase IV — Live Progress

**3 / 8 completed · 37.5% · AETHER-107 accepted.**

| Turn | Bound | Status | Completion |
|---|---|---|---:|
| 1 | 105 Bounded observation economy | **Accepted (synthetic)** | **12.5%** |
| 2 | 106 Sequential calibration | **Accepted (synthetic)** | **25%** |
| 3 | 107 Temporal risk budgeting | **Accepted (synthetic)** | **37.5%** |
| 4 | 108 Sparse-sensor resilience | Planned | 37.5% |
| 5 | 109 Recovery | Planned | 37.5% |
| 6 | 110 Deterministic resource scheduling | Planned | 37.5% |
| 7 | 111 Unseen dynamic stress | Planned | 37.5% |
| 8 | 112 Phase freeze | Planned | 37.5% |

## Turn 3 — AETHER-107

- 300 seeded episodes per environment × 4 environments × 24 decisions = **28,800 decisions per controller**.
- Alpha spending: `0.05 / [t(t+1)]`, total **0.048** across 24 decisions.
- Fixed-time per-tick 95% confidence produced **246/1,200 episodes** with at least one unsafe authorization.
- Budgeted, independent-root-aware upper bounds produced **0/1,200 observed unsafe episodes**; this is not proof of zero underlying risk.
- In the stable IID environment, the budgeted controller still authorized **6,045/7,200** ticks.
- For 560 correlated reports representing 56 independent roots, the controller authorized **0** ticks; utility penalty preserved explicitly.
- Illustrative total cost **343,200** budgeted vs **353,527.5** per-tick baseline.
- [Source, evidence and interactive lab](107/) committed. Live GitHub Pages deployment not independently verified.
- **Phase IV: 37.5% complete. Next AETHER-108: sparse-sensor resilience.**

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
