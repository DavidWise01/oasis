# AETHER-096B — Conservative Context Recognition

**Phase II Turn 1: ACCEPTED — 1/8 = 12.5% complete.**

AETHER-096 failed a false-promotion constraint on its first evaluation. AETHER-096B preserves that evidence, retains the same observed-only random-forest feature family, and chooses a stricter **threshold 0.72** on separate validation seeds before testing fresh holdout seeds.

## Study design

- Same six synthetic regimes: stable, step, ramp, burst, asymmetric burst, oscillatory shift.
- Training seeds **96001–96032**, validation **96101–96124**, new holdout **96301–96340**.
- Detector features: current and prior 11 audit error counts, derived moments, extremes, temporal differences. The true regime is **not** an input during operation; used only as supervised training label and audit truth.
- Validation rule fixed before new holdout: select the lowest probability threshold with nonburst false positive rate ≤0.5% and burst recall ≥3%.
- Evaluation acceptance rule: nonburst false promotions ≤1%, burst recall ≥3%, total cost no more than rolling baseline. All three passed in this simulation.

## Held-out evidence

| Statistic | Result |
|---|---:|
| Selected threshold | 0.72 |
| Nonburst false promotions | **61 / 14,400 (0.4236%)** |
| Burst recall | **508 / 2,880 (17.6389%)** |
| Rolling baseline cost | 123,417.0 |
| Context-gated cost | **123,144.7** |
| Savings | **272.3 units (0.2206%)** |
| Rolling wrong actions | 6,771 |
| Context-gated wrong actions | 6,694 |
| Context-gated sentinel probes | 369 |
| Authorized ticks, rolling / context | 13,078 / 13,051 |

Cost = 10 per wrong action + 0.05 per withheld action + 0.01 per labeled observation. The oracle burst comparator has unavailable true labels, and is a diagnostic only. The observed conditional gate is the only eligible learned strategy, and fallback remains rolling-only when the context is not verified.

### Limitations

- Small improvement; no seed-level confidence interval or field validation yet.
- Synthetic independent audit roots by construction only; no distribution-free control on false classifications.
- AETHER-097 must handle contradictions and changing context; mid-run permission revocation has **not** been established.
- Phase credit is for the *narrow predefined 096 context-detection gate*, not for a production-certified system.

### Reproduction

Run `python aether/096b/experiment.py` using NumPy, SciPy, scikit-learn. Regenerates `seed_results.csv`, `results.csv`, `context_confusion.csv` and `manifest.json`.

[Interactive GitHub Pages report](https://davidwise01.github.io/oasis/aether/096b/) · [Failed 096 result](../096/) · [Phase tracker](../PHASE-II-STATUS.md)

**Next — AETHER-097:** Context contradictions. Identify cases where earlier observed evidence supports burst, but new observations overturn it. Preserve the counterexample, remove stale permission, and retest under unseen change points.

`{24/[2]/[4]/(3)/(3)/(1)/(1)} · {{i}} · .dlw`
