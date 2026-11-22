# AETHER-109B — Cost-Neutral Fresh Reauthorization

**Phase IV · Turn 5 of 8 — ACCEPTED on synthetic holdout. Phase progress: 62.5%.**

## Invariant

A controller may not reuse a pre-outage certificate to authorize an action after observations resume. Two genuinely fresh post-resume audits must establish admissibility. Previous evidence remains immutable history, not current authority.

## Procedure

AETHER-109 previously failed because fresh reauthorization cost 10 additional units in a safe recovery regime. For 109B, choose the number of independent roots per post-resume audit from **480, 500, 520, 540, 560** using **30 development seeds (109201–109230)** for each scenario. Choose the passing policy with largest net cost savings on that development set. Selected: **480 independent roots per batch**.

Evaluate on **100 untouched seeds (109301–109400)** per scenario, four scenarios with 30 ticks per episode. Paired policies see the same canonical generated independent root sequence and held-out action outcomes. The fresh policy uses the first 480 roots after resumption; the stale baseline uses 560.

Four simulated scenarios: safe resume; hazard appearing immediately on resume; delayed report; tenfold duplicate report flood. Delayed/duplicate observations are not used as new roots. The stale baseline intentionally reuses outdated permission for three ticks post-outage, making it a deliberately unsafe reference, not an endorsed controller.

Fixed-time one-sided Clopper–Pearson bounds with per-tick allocation `0.05/30` and risk cutoff 2.5% are used on two recent audit batches. The true risk used to generate outcomes is never available to the runtime selector.

## Held-out results

| Scenario | Stale cost | Fresh optimized cost | Savings |
|---|---:|---:|---:|
| Safe resume | 29,240 | **27,860** | 1,380 |
| Hazard at resume | 60,040 | **29,480** | 30,560 |
| Delayed delivery | 57,410 | **28,957.5** | 28,452.5 |
| Duplicate flood | 30,930 | **29,460** | 1,470 |
| **Total** | **177,620** | **115,757.5** | **61,862.5** |

Unsafe authorized ticks: **600 stale versus 0 fresh**. Mean first safe action delay in the safe resume environment: **0 ticks stale versus 1 tick fresh**. ACT ticks in that environment: **2,200 for both policies**. Overall ACT ticks: 8,000 stale versus 7,399 fresh, reflecting removal of invalid immediate post-outage authorization.

Acceptance gate, fixed before holdout: lower unsafe authorization; no per-regime cost regression; mean safe restart delay at most three ticks; preserve safe-regime usefulness within 8% tolerance. **All pass.**

## Limitations

Results are synthetic and rely on independent Bernoulli roots and known outage timing. The stale comparator is purposefully unsafe. The risk bound is not automatically valid under unknown dependence, adaptive timing or changing distributions. The model demonstrates a feasible design and bounded synthetic cost, not production safety or statistically universal reliability.

## Reproduce

`python aether/109b/experiment.py` requires Python, NumPy and SciPy. Generates `development_options.csv`, `results.csv`, `seed_results.csv`, `trace_samples.csv`, `manifest.json`. The previously failed [AETHER-109](../109/) record remains append-only.

[Interactive Pages-ready lab](https://davidwise01.github.io/oasis/aether/109b/) · [Phase IV tracker](../PHASE-IV-STATUS.md).

**Next natural bound — AETHER-110: Deterministic Resource Scheduling.** Test choice of evidence expenditure under constrained budgets with one canonical controller, accounting for opportunity cost and irreversible risk.

`{24/[2]/[4]/(3)/(3)/(1)/(1)} · {{i}} · .dlw`
