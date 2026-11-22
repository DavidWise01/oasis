# AETHER-106 — Sequential Calibration Under Adaptive Sampling

**Phase IV / Turn 2 of 8 — Accepted within synthetic test scope. 25% completion.**

## Question
Can the controller purchase evidence in stages without treating an ordinary fixed-time 95% binomial upper confidence bound as valid at whichever stage looks favorable? What happens if ten reported observations originate from one shared Bernoulli root?

## Simulation
- **500 independent seeded cases** for each of four true risks: 0.3%, 1.8%, 3.5%, 6.5%.
- Two modes: IID Bernoulli observations and block-correlated observations (ten identical reports from one independent draw).
- Four potential looks: 40, 140, 280, 560 reported observations.
- 2.5% action risk limit. The true risk is used only by the evaluator, not the online controller.
- Four policies: ordinary fixed-sample Clopper–Pearson; naive repeated looks at the same 95% bound; four-look alpha-spent Clopper–Pearson assuming every reported observation is independent; and **four-look alpha-spent, root-aware Clopper–Pearson** counting ten identical correlated reports as one effective observation.

Each per-look bound uses one-sided Clopper–Pearson with **alpha = 0.05 / 4**. The Bonferroni union bound controls the probability of any falsely low upper bound at the four inspection points **if the counted roots are IID Bernoulli with a fixed probability**. This is not a guarantee under arbitrarily evolving risk, unknown cross-root dependence, or infinitely repeated episodes.

## Held-out results (500 cases per condition)

| Condition | Policy | ACT | Unsafe ACT |
|---|---|---:|---:|
| IID, true risk 0.3% | root-aware sequential | 493 | 0 |
| IID, true risk 3.5% | naive repeated 95% | 6 | 6 |
| IID, true risk 3.5% | root-aware sequential | 1 | **1** |
| Correlated blocks, true risk 0.3% | naive repeated 95% | 476 | 0 |
| Correlated blocks, true risk 0.3% | root-aware sequential | **0** | 0 |
| Correlated blocks, true risk 3.5% | naive repeated 95% | 313 | **313** |
| Correlated blocks, true risk 3.5% | root-aware sequential | 0 | **0** |

**Acceptance gate:** root-aware sequential safe IID ACT ≥250/500; risky IID and block10 false approvals ≤20/500 for each 3.5% and 6.5% stress; and correlated risky false approvals fewer than naive optional at 3.5%. All passed.

## Significant limitation
The block-aware rule is extremely conservative under known correlation: **zero useful actions** at 0.3% true risk. With 560 reported observations, only 56 independent blocks exist. The test establishes trustworthy *accounting* of observation count under this specific dependency model, not efficient operation in all contexts.

## Reproduction
`python aether/106/experiment.py` with SciPy. The script writes `results.csv`, `seed_results.csv`, `trace_samples.csv` and `manifest.json`. Actual evaluation source and summary are preserved here. Input seeds: 106001–106500. No hidden regime labels enter action selection.

The single governing rule is: **HOLD until an alpha-spent, independence-adjusted bound certifies ACT admissibility**. No quorum, source voting, or Byzantine model is introduced.

[Interactive lab](https://davidwise01.github.io/oasis/aether/106/) · [Phase IV progress](../PHASE-IV-STATUS.md) · [Prior AETHER-105](../105/)

**Next AETHER-107 — Temporal Risk Budgeting:** An across-episode certificate and evidence-spending policy, tested under repeated stopping and hazard shifts.

`{24/[2]/[4]/(3)/(3)/(1)/(1)} · {{i}} · .dlw`
