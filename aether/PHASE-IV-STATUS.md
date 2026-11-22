# AETHER Phase IV — Live Progress

**5 / 8 completed · 62.5% · AETHER-109B accepted on untouched synthetic holdout.**

| Turn | Bound | Status | Completion |
|---|---|---|---:|
| 1 | 105 Bounded observation economy | **Accepted (synthetic)** | **12.5%** |
| 2 | 106 Sequential calibration | **Accepted (synthetic)** | **25%** |
| 3 | 107 Temporal risk budgeting | **Accepted (synthetic)** | **37.5%** |
| 4 | 108 Sparse-sensor resilience | **Accepted (synthetic)** | **50%** |
| 5 | 109 Recovery | **Accepted via 109B** | **62.5%** |
| 6 | 110 Deterministic resource scheduling | Planned | 62.5% |
| 7 | 111 Unseen dynamic stress | Planned | 62.5% |
| 8 | 112 Phase freeze | Planned | 62.5% |

## Turn 5 correction — AETHER-109B (accepted)

- AETHER-109 failed its original no-per-environment-cost-regression criterion and remains preserved unmodified.
- AETHER-109B picked **480 roots per resumed audit** from options 480, 500, 520, 540, 560 on separate development seeds **109201–109230**.
- Independent holdout **109301–109400** × four scenarios × 30 ticks: 400 paired episodes.
- The revised policy required **two fresh post-outage batches**; stale certificates never authorize resumption.
- **Unsafe authorization: 600 stale → 0 fresh** in this synthetic mixture.
- **Cost: 177,620 stale → 115,757.5 fresh**, saving **61,862.5**. Every scenario improved, including safe resume **29,240 → 27,860**.
- Safe-resume ACT count 2,200 for both policies and first safe ACT delay 1 tick fresh versus 0 stale; all four gates passed.
- Synthetic Bernoulli roots, fixed outages, and deliberately unsafe stale comparator limit generalization.
- [Accepted 109B source and results](109b/). The original [failed 109 evidence](109/) remains immutable in its own folder.
- **Actual Phase IV completion: 5 of 8 = 62.5%. Next: AETHER-110 deterministic resource scheduling.**

## Turn 5 — AETHER-109 (failed; preserved diagnostic)

- 100 paired seeds × 4 regimes × 30 ticks = **12,000 decision opportunities per policy**.
- Stale pre-outage certificate reauthorization caused **600 unsafe authorized ticks**; two genuinely fresh post-outage batches reduced this to **0** in simulation.
- Combined cost fell from **179,060 to 123,000**.
- **The strict no-regime-regression condition FAILED:** safe-resume cost rose **29,660 → 29,670**, despite favorable aggregate results.
- Fresh recovery produced one-tick safe-resume delay rather than immediate stale authorization. Out-of-date and duplicate observations were ignored.
- An initial in-memory prototype double-added a fresh batch to the certificate. Corrected and retested before publishing.
- [AETHER-109 source and failed gate](109/) archived. Phase remains **4/8 = 50%**; next AETHER-109B must use fresh independent evaluation seeds.

## Turn 4 — AETHER-108

- 120 synthetic seeds per environment × 5 environments × 24 ticks = **14,400 paired decision opportunities**.
- Both policies issued exactly **3,489 ACT** and **10,911 HOLD** decisions, with zero paired mismatches.
- Economical acquisition saved **582,680 independent roots**, from 4,730,880 down to 4,148,200 (**12.3%**).
- Synthetic cost dropped from **144,211.3 to 138,384.5**, saving **5,826.8**.
- No additional unsafe authorizations; **0** unsafe authorized inspection ticks were observed for either policy.
- Delayed and duplicated reports were not admitted as fresh evidence. The tenfold-correlated scenario still generated **zero ACT** decisions due to insufficient independent samples.
- [Executable experiment and Pages-ready report](108/) committed. Live Pages deployment remains unverified.
- **Phase IV: 50% complete. Next AETHER-109: fresh-evidence recovery after sensing resumes.**

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
