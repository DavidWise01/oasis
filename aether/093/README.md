# AETHER-093 — Risk-Weighted Sentinel Allocation

**Invariant 093:** A warning must justify not only its accuracy, but the marginal cost of its next observation.

## Separate selection and evaluation

The Python experiment enumerates eight Boolean combinations of whether to purchase a sentinel sample in three observed audit states: quiet, uncertain or already denied. The choices are evaluated using 24 training seeds in each of three simulator regimes (stable, abrupt step and gradual ramp), and the lowest training cost is frozen **before** held-out testing.

The selected policy is **quiet: no probe; uncertain: probe; denied: no probe**. The selected policy was then tested on 40 new seeds per regime and a newly introduced burst-pattern mechanism, with randomized change times and levels. There are 72 ticks per trial, 140 audit labels and 150 held-out action outcomes per tick; each sentinel purchase adds 80 labels.

The tested controls are rolling-only (zero sentinel), periodic (every fifth tick), continuous (every tick), and the trained contextual policy. All policy branches receive the **same pre-generated random outcomes** within a seed/regime pair. Conditional risk uses a retrospective Clopper-Pearson upper bound on the five most recent 140-label audit batches.

## Held-out results — illustrative total loss

| Environment | Rolling | Periodic | Continuous | Learned |
|---|---:|---:|---:|---:|
| Stable | **17,289.5** | 17,779.5 | 19,643.5 | 17,473.5 |
| Abrupt step | 21,304.5 | 21,519.5 | 22,736.0 | **20,864.4** |
| Gradual ramp | **21,019.5** | 21,332.0 | 22,906.0 | 21,174.7 |
| Unseen bursts | 22,517.0 | 22,587.0 | 23,181.0 | **21,535.9** |
| **Total** | 82,130.5 | 83,218.0 | 88,466.5 | **81,048.5** |

Cost = 10 wrong action + 0.05 withheld action + 0.01 purchased label. The learned policy saves **1,082 cost units (1.32%)** versus rolling-only, reduces wrong actions from 4,996 to 4,656, and purchases 2,035 of 11,520 possible sentinel probes. Continuous monitoring has the lowest unsafe authorized inspection count (63 versus 72 for learned) but is more expensive.

This is the first positive out-of-sample aggregate cost result in the AETHER sentinel series. **It is not universal dominance**: the learned policy is worse in stable and gradual-ramp scenarios. The error reduction is partly paid for through increased abstention. No across-seed confidence interval has yet been established.

## Reproduce

`python aether/093/experiment.py` (NumPy and SciPy required) generates `results.csv`, `tick_audit.csv`, `training_options.csv`, and `manifest.json`. The checked-in summary CSV corresponds to the recorded run. Run the executable to generate full audits.

## Evidence limits

- These are synthetic Bernoulli observations, not real instruments.
- The learned policy searches eight rules on training data; the held-out evaluation uses new seeds but remains a limited simulator family.
- The new burst pattern differs from training patterns, but this does **not** imply robustness to all unseen mechanisms.
- The confidence bound concerns past audit outcomes. It does not guarantee current or future risk immediately after drift.
- A per-seed paired bootstrap or other uncertainty analysis is needed before treating the 1.32% observed gain as dependable.

[Interactive Pages lab](https://davidwise01.github.io/oasis/aether/093/) · [Previous bound AETHER-092](../092/)

## Next natural bound — AETHER-094: Generalization Confidence and Regret

Measure paired seed-level uncertainty in the learned policy's cost advantage, stress it with new adversarial noise families and shifted label costs, and authorize policy deployment only when a conservative lower confidence bound on the improvement is positive. Retain rolling-only as a safe fallback.

`{24/[2]/[4]/(3)/(3)/(1)/(1)} · {{i}} · .dlw`
