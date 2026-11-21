# AETHER-089 — Online Lineage-Aware Confidence Sequences

**Invariant 089:** Independent evidence must remain independently identifiable, and yesterday's statistical permission must not automatically authorize tomorrow's decisions.

## Reproducible synthetic experiment

Run `python aether/089/experiment.py` with Python, NumPy and SciPy. The script writes `results.csv`, `look_audit.csv` and `manifest.json` next to itself.

- Seed 89089, 500 trials per scenario, 30 looks per trial, 60 independent Bernoulli evidence roots at each look.
- Six exact duplicate records per root, to test ancestry miscounting.
- Three environments: stationary safe (0.25% failure), stationary unsafe (6%), and abrupt drift from 0.25% to 6% **after look 15**.
- Conditional error budget: 2%. Each root is a labeled, independent Bernoulli error observation.
- Three controllers: naive repeated inspection treating copies as independent, unique-root cumulative exact Clopper-Pearson upper bounds with alpha/30 per look, and unique-root last-8-look bounds with the same alpha spending.

## Key results for the drift experiment

| Controller | Pre-drift authorization | Post-drift authorization | Unsafe post-drift inspections |
|---|---:|---:|---:|
| Naive copied evidence | 98.71% | 31.99% | 2,399 |
| Unique roots, cumulative | 52.04% | 8.65% | 649 |
| Unique roots, recent 8-look window | 39.29% | **0.32%** | **24** |

The rolling model reduces post-shift incorrect permission **96.3% versus cumulative unique-root calibration**, at the cost of lower authorization during stationary safe conditions. On the latter half of stationary safe trials the cumulative model authorizes 100% of inspections, while the rolling model authorizes 65.73%.

## What the statistics do and do not establish

Bonferroni alpha spending across 30 prespecified looks addresses repeated tests under the underlying fixed-risk Bernoulli model. Root deduplication prevents counting verbatim copies as independent evidence. A sliding-window bound concerns the *average risk in that recent window*, under relevant independence/stationarity conditions; it **does not guarantee safety for the next observation** when the environment changes. The earliest post-drift authorizations are still unsafe, and hidden partial ancestry, correlated source roots and adversarial drift were not simulated here.

This is a controlled counterexample demonstration, not a real instrument certification. The study does not establish a uniform 2% bound under nonstationarity.

## GitHub Pages

[Interactive AETHER-089 report](https://davidwise01.github.io/oasis/aether/089/) · [Previous AETHER-088](../088/)

## Next natural bound — AETHER-090

**Preemptive Drift Detection and Conditional Reauthorization.** Add separate sentinel probes to detect a change before using a stale certificate, measure worst-case unsafe exposure at the change boundary, and allow a return to operation after evidence reestablishes current-risk control.

**Invariant 090 candidate:** Reauthorization must require evidence about the current regime; evidence of a past safe regime cannot substitute for evidence of present safety.

`{24/[2]/[4]/(3)/(3)/(1)/(1)} · {{i}} · .dlw`
