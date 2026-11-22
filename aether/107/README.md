# AETHER-107 — Temporal Risk Budgeting

**Phase IV · Turn 3 of 8 · Accepted in synthetic tests · target 37.5%.**

## Invariant 107

Permission to make repeated decisions must use a **finite familywise error allowance**, not independently reuse a fixed 5% false-certification allowance at every tick.

One deterministic controller, one-way evidence. **ACT** if a one-sided Clopper–Pearson upper bound certifies risk at most **0.025**. Otherwise **HOLD**. The root-aware controller counts independent observations; groups of ten identical reports are treated as **one root**. Hidden true risk is never used for action selection.

## Simulation

- **300 paired seeds per scenario**, 4 scenarios; 1,200 episodes per policy, 24 decisions per episode.
- Scenarios: safe IID Bernoulli, hazard transition, oscillating risk, and tenfold copied observations with a hazard transition.
- 560 observed reports per tick; in the duplicated case only 56 genuinely independent roots.
- Three compared policies: per-tick nominal 95%, alpha-spending without root correction, alpha-spending with root correction.
- Finite alpha budget: `alpha_t = 0.05 / [t(t+1)]` for `t=1,...,24`, total **0.048**, below **0.05**.
- Root-aware bounds require independence **between source roots within a tick** as constructed. The union-bound logic also requires correct per-tick binomial sampling assumptions.

## Held-out results

| Scenario | Per-tick baseline episodes with unsafe ACT | Spent root-aware |
|---|---:|---:|
| Safe IID | 0 / 300 | 0 / 300 |
| Hazard transition | 3 / 300 | 0 / 300 |
| Oscillating risk | 2 / 300 | 0 / 300 |
| Copied roots | 241 / 300 | **0 / 300** |
| All | **246 / 1,200** | **0 / 1,200** |

Other metrics:
- Total cost: **353,527.5** baseline vs **343,200.0** spent root-aware, saving **10,327.5** illustrative units.
- Stable independent safe environment: **6,045 ACT / 7,200 ticks** with root-aware spending, vs 7,198 baseline.
- Copied-root environment: **0 ACT / 7,200 ticks** with root-aware spending, due to insufficient independent sample size. This is a real utility limitation.
- Alpha spending without root awareness still permitted unsafe ACT in **241/300 correlated episodes**; temporal budgeting alone does not cure false independence.

## Acceptance gate

1. At most 25 of 300 episodes with any unsafe ACT for every risky scenario: **PASS** (all zero).
2. At least 1,000 safe-IID ACT ticks: **PASS** (6,045).
3. Fewer risky false-approval episodes than per-tick 95%: **PASS**.
4. No worse than naive alpha spending on each risky scenario: **PASS**.

**Result: accepted for the narrow synthetic benchmark.** This is not an experimental proof that real-world failure probability is zero. The observed 0/300 is compatible with nonzero rates.

## Reproduce

```bash
python aether/107/experiment.py
```

Requires NumPy and SciPy. The code regenerates `results.csv`, `seed_results.csv`, `trace_samples.csv`, and `manifest.json`. Deterministic hashed seed derivation makes the path repeatable.

## Limits

The simulator supplies accurate root grouping by construction. Unknown dependence, common-mode failures, forged ancestry, non-Bernoulli errors, and within-tick drift are not covered. Risk can shift across ticks; the confidence budget is finite across 24 ticks, not an unlimited anytime guarantee. In strongly correlated settings, utility collapses to HOLD. This must be addressed in AETHER-108 rather than treated as complete autonomy.

[Interactive Pages report](https://davidwise01.github.io/oasis/aether/107/) · [Phase IV tracker](../PHASE-IV-STATUS.md) · [Previous AETHER-106](../106/)

**Next — AETHER-108: Sparse-Sensor Resilience.** Test missing observation roots and bounded recovery without pretending duplicates are independent.

`{24/[2]/[4]/(3)/(3)/(1)/(1)} · {{i}} · .dlw`
