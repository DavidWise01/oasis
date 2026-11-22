# AETHER-092 — Adaptive Sentinel Scheduling

**Invariant 092:** A warning system should spend evidence where it changes decisions, preserving resources when existing evidence is sufficient.

This module extends AETHER-091 with four paired monitoring policies. The synthetic simulator uses 40 independent seeds per scenario, 90 ticks per seed, 140 fresh audit labels, 150 independent decision-test outcomes per tick, and up to 80 additional sentinel labels per probe.

## Four controllers

1. **Rolling-only:** no sentinel, last-five-batch Clopper-Pearson audit bound.
2. **Continuous:** 80 sentinel labels every tick.
3. **Periodic:** 80 sentinel labels every fifth tick.
4. **Adaptive:** 80 sentinel labels every tenth tick or when the audit upper bound lies in [0.010,0.035], or when at least two audit failures appear in a tick.

Sentinel alarms use a predeclared threshold of three observed errors. When an alarm occurs, permission is suspended; five recent audit batches must clear the gate for reauthorization.

All four policies encounter *identical*, pregenerated audit, sentinel and held-out action draws for each paired seed. Results are not selected from policy outcomes during training; the adaptive rule is prespecified and heuristic.

## Results over 40 × 90 ticks per scenario

| Scenario | Rolling cost | Continuous cost | Periodic cost | Adaptive cost |
|---|---:|---:|---:|---:|
| Stable safe (0.3%) | **20,862.50** | 23,832.50 | 21,438.50 | 22,174.50 |
| Subtle drift (0.3% → 2.6%) | **26,575.00** | 28,552.50 | 27,131.00 | 27,531.10 |
| Moderate drift (0.3% → 3.8%) | **26,612.50** | 28,677.50 | 27,196.00 | 27,720.40 |

Under subtle drift, wrong authorized actions: rolling 1,177; continuous 1,041; periodic 1,166; adaptive 1,053. Under moderate drift: 1,132; 1,025; 1,132; and 1,032.

Adaptive sentinel monitoring uses 1,615 of 3,600 possible probes under stable safety (55.1% fewer than continuous), 2,267 under subtle drift (37.0% fewer), and 2,438 under moderate drift (32.3% fewer). Nevertheless, **rolling-only is the cheapest controller in every tested scenario**.

Cost = 10 per incorrect authorized action + 0.05 per withheld action + 0.01 per labeled observation. Other cost ratios could reverse the ranking.

## Reproduction

Run `python aether/092/experiment.py` with NumPy and SciPy. It generates `results.csv`, `tick_audit.csv`, `events.csv` and `manifest.json`. The checked-in `results.csv` summarizes the all-tick outcomes; run the script to regenerate the entire detailed audit.

## Limitations

- Synthetic independent Bernoulli evidence roots, not physical or production observations.
- Conditional risk bounds refer to recent samples; they are not proven anytime-valid under changing environments.
- Sentinel thresholds were calibrated under nominal safe noise, not arbitrary distribution shift.
- The scheduling rule is prespecified, not learned from an independently evaluated value-of-information model.
- Fewer wrong authorized decisions can reflect higher abstention; report authorization and cost alongside errors.

[Interactive GitHub Pages report](https://davidwise01.github.io/oasis/aether/092/) · [Previous AETHER-091](../091/)

## Next natural bound — AETHER-093: Risk-Weighted Sentinel Allocation

Learn the marginal value of another probe from independent training regimes, test on unseen drift shapes and randomized change times, and permit *zero* sentinel spending unless the estimated benefit exceeds its cost. Compare the adaptive policy to the simple rolling and periodic baselines without post-hoc tuning on the evaluation set.

**Invariant 093 candidate:** A warning must justify not only its accuracy, but the marginal cost of its next observation.

`{24/[2]/[4]/(3)/(3)/(1)/(1)} · {{i}} · .dlw`
