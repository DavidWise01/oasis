# AETHER-102B — Guard-Effectiveness Drift Detection

**Phase II Turn 7 of 8: Accepted against the frozen synthetic acceptance gate. 87.5% complete.**

## Problem and correction

[AETHER-102](../102/) exposed a guard-degradation counterexample: the unmonitored AETHER-101 selector lost 443.2 illustrative cost units to direct-only on one unseen regime. AETHER-102B adds an **observable noisy guard-health diagnostic** that is purchased only when the frozen selector proposes GUARDED. The guard-health signal is measured at the current tick; the controller is not supplied with the hidden simulation parameter or regime label.

One governing action path:

1. The frozen current-window audit risk gate must first allow active action. Otherwise select **HOLD**.
2. If the frozen policy proposes GUARDED, sample guard health. If reading exceeds development-selected threshold **1.15**, select **DIRECT**.
3. Otherwise retain the frozen decision. Append a hash-linked event record. No earlier event is modified.

The diagnostic costs **0.08 units per sample**, modeled as effectiveness plus zero-mean Gaussian noise with SD **0.25**. Its existence and calibration are assumptions of this synthetic simulation, **not properties verified for real hardware**.

## Separation of selection and evaluation

- Development seeds: 102301–102320 (20 per regime).
- Candidate thresholds: 0.65, 0.75, 0.85, 0.95, 1.05, 1.15, 1.25.
- Selection: minimum development total cost among thresholds avoiding a cost regression versus direct-only in every development regime. This selected 1.15 before evaluation.
- New held-out seeds: 102401–102480 (80 per regime).
- Five environments: flash hazard, scarce audits, frequency chirp, degraded guard effectiveness, and correlated audit noise.
- 400 paired cases × 96 ticks = **38,400 ticks per controller**.

## Untouched evaluation results

| Regime | Direct-only cost | Monitored cost | Savings |
|---|---:|---:|---:|
| Flash hazard | 57,857.50 | 57,504.22 | **353.28** |
| Scarce audits | 59,922.50 | 58,880.38 | **1,042.12** |
| Frequency chirp | 70,941.50 | 67,814.54 | **3,126.96** |
| Guard degradation | 66,258.50 | 65,320.74 | **937.76** |
| Correlated audit | 71,550.00 | 67,879.92 | **3,670.08** |
| **All** | **326,530.00** | **317,399.80** | **9,130.20** |

Unmonitored selector total: **317,915.00**. Monitoring improves on it by **515.20** units across all scenarios, but is slightly costlier than unmonitored in the four non-degraded scenarios due to diagnostics.

Unsafe authorized ticks: **288** for each of direct-only, frozen selector, and monitored selector. Monitored guarded decisions: **523**, compared with 575 unmonitored. Incorrect authorized outcomes: **9,386** monitored, versus 10,335 direct-only and 9,439 frozen selector.

## Acceptance

- No held-out environment has greater monitored cost than direct-only: **PASS**.
- Overall monitored cost <= direct-only: **PASS**.
- No increase in unsafe authorization versus direct-only: **PASS**.
- Four deterministic test types (replay, prefix equality, hash integrity, admissibility) × 400 cases = **1,600/1,600 PASS**.

## Limitations

This is an in-distribution holdout across five already defined scenario families, not a proof for arbitrary new environments. It assumes a usable contemporaneous noisy guard-health sensor, so the result cannot demonstrate learning guard effectiveness merely from outcomes in the absence of such an observable. The fixed-time binomial upper bound is retrospective and may fail under drift. The hash chain is an internal integrity check, not proof of trusted external custody. The causal-prefix check repeats the same observation stream; it is not a separate counterfactual future perturbation test.

## Reproduction

`python aether/102b/experiment.py` (requires NumPy and SciPy). This file is self-contained and reproduces `development_options.csv`, `results.csv`, `seed_results.csv`, `trace_samples.csv`, and `manifest.json`.

[Pages-ready interactive report](https://davidwise01.github.io/oasis/aether/102b/) · [Phase tracker](../PHASE-II-STATUS.md)

**Next AETHER-103 — Integration, reproducibility and phase freeze.** That final turn will verify the complete phase, preserve counterexamples and close Phase II rather than expanding into distributed agreement or Byzantine work.

`{24/[2]/[4]/(3)/(3)/(1)/(1)} · {{i}} · .dlw`
