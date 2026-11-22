# AETHER-091 — Subtle-Drift Value of Warning

**Invariant 091:** An additional warning mechanism earns its place only when the decisions it improves justify the evidence it consumes.

## Experiment

Reproducible synthetic Bernoulli-risk experiment using 40 paired seeds in each of three scenarios, 90 ticks per seed, 140 fresh audit labels and 150 separate held-out action samples per tick. The sentinel policy buys another 80 independent labels each tick. Both policies see the same underlying random outcomes within each paired trial.

Environmental phases: ticks 1–30 safe at 0.3% wrong-action risk; ticks 31–60 change to either 2.6% (**near limit**), 3.8% (**moderate**), or remain 0.3% (**no drift**); ticks 61–90 return to 0.3%.

The rolling-only baseline uses a five-batch audit window, a one-sided fixed-time 95% Clopper-Pearson upper confidence bound, and a 2% permission threshold. The sentinel policy adds an independent 80-label probe, raises an alarm on at least three sentinel errors, suspends permission and reauthorizes after five recent audit batches meet the confidence test. The alarm threshold was selected from the 0.3% safe-reference model, not from held-out outcomes.

## Shift-phase outcomes (40 seeds per scenario)

| Shift | Rolling wrong actions | Sentinel wrong actions | Rolling authorized ticks | Sentinel authorized ticks |
|---|---:|---:|---:|---:|
| 0.3% to 2.6% | 263 | 154 | 64 | 35 |
| 0.3% to 3.8% | 143 | 40 | 25 | 7 |
| No shift | 510 | 506 | 1199 | 1191 |

## Full 90-tick-cycle economic cost

Illustrative cost = 10 per wrong action + 0.05 per withheld action + 0.01 per acquired evidence label.

| Scenario | Rolling cost | Sentinel cost |
|---|---:| ---:|
| Near limit | 27,555 | 29,607.5 |
| Moderate | 26,375 | 28,457.5 |
| Stable safe | 20,862.5 | 23,832.5 |

The sentinel lowers wrong authorizations during shifts but is economically worse under the declared costs. It purchases 792,000 rather than 504,000 labels per scenario (57.1% more). This is a **negative economic result** under the stated assumptions, not an argument that warnings are intrinsically bad.

The near-limit scenario detected drift in all 40 seeds; 13 of 40 detected on the first shifted tick, with mean detection delay 2.325 ticks. The moderate scenario also detected all 40, with 24 detections on the first tick and mean delay 0.65 ticks. There were 3 and 7 false alarms during safe phases, respectively.

## Evidence and limits

Data are simulated; costs are illustrative. A fixed-time confidence bound from recent data is not anytime-valid and cannot certify the next unseen risk following a regime change. A warning does not retroactively prevent already authorized decisions. Independent roots are a property of the generator, not demonstrated provenance in field data.

Run `python aether/091/experiment.py` (requires NumPy and SciPy) to generate per-tick and summary CSV results.

[Interactive report](https://davidwise01.github.io/oasis/aether/091/) · [Previous 090](../090/)

## Next natural bound — AETHER-092: Adaptive Sentinel Scheduling

Instead of buying 80 extra labels on every tick, allocate a sentinel budget only when the expected risk reduction justifies it; evaluate sequential and sparse sentinels across subtle drift and stationary safety. Require independent held-out policy evaluation and explicit costs of missed detection.

`{24/[2]/[4]/(3)/(3)/(1)/(1)} · {{i}} · .dlw`
