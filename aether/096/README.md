# AETHER-096 — Context Detection (Phase II / Turn 1)

**Status: FAILED PROMOTION GATE. Phase completion: 0/8 (0%).** This is an executed diagnostic experiment, not a finished promotion-capable bound.

## Governing invariant

A conditional promotion may be based on observations about the environment, not on a hidden simulator-provided environment label. The single governing controller retains **rolling-only** as its best admissible policy until independent evidence supports another choice.

## Synthetic experiment

- Six environments: stable, abrupt step, ramp, periodic burst, asymmetric burst, oscillatory shift.
- Entirely disjoint seeds: 32 training seeds per environment (96001–96032), 24 validation seeds (96101–96124), and 40 holdout seeds (96201–96240).
- 72 ticks per episode, 140 observed audit labels, 80 optional sentinel labels, and 150 independent decision outcome labels per tick.
- Context features derived solely from current and preceding 11 audit-error counts: recent trajectory, mean, variability, extremes, directional change. **No true environment label enters the runtime feature vector.**
- Random forest: 100 trees, depth 7, minimum leaf size 25. A probability threshold of 0.70 was selected on validation data under a maximum 1% nonburst false-classification rate.
- Model output determines whether the burst-specific learned sentinel is eligible. Rolling-only and an *unavailable oracle with access to true context* are comparison baselines, not additional governing authorities.

## Independent holdout results

| Context classification | Total | Predicted burst |
|---|---:|---:|
| Nonburst | 14,400 | 195 (1.3542% false promotions) |
| Burst | 2,880 | 618 (21.4583% recall) |

| Policy | Overall cost | Wrong actions | Extra sentinel probes | Authorized ticks |
|---|---:|---:|---:|---:|
| Rolling-only | **125,137.0** | 6,901 | 0 | 13,022 |
| Context-gated sentinel | 125,190.0 | 6,850 | 535 | 13,004 |
| Oracle burst label (unavailable) | 124,747.2 | 6,776 | 794 | 12,992 |

The observed context classifier **fails** the 1% nonburst false-promotion criterion and increases total cost by **53** compared with rolling-only. Its lower wrong-action count is partly due to additional withheld decisions and purchased evidence.

The oracle result indicates potential value if the correct context were known, but using the oracle as the operational controller would violate the problem.

## Phase gate and next action

**No turn credit.** Under the frozen phase contract, a failed bound does not advance the tracker. The next turn remains AETHER-096 and should improve or conservatively abstain on uncertain context, with a new independent holdout. It should not jump ahead to AETHER-097 or invoke quorum, witness agreement or Byzantine machinery.

The experiment's risk estimates are **retrospective** and are not guarantees under unmodeled drift or correlated evidence. Source ancestry is independent only by construction.

### Reproduce

`python aether/096/experiment.py` (NumPy, SciPy, scikit-learn). Outputs `results.csv`, `context_confusion.csv`, `seed_results.csv`, `manifest.json`.

[Interactive GitHub Pages-ready lab](https://davidwise01.github.io/oasis/aether/096/) · [Phase charter](../PHASE-II-096-103.md) · [Previous AETHER-095](../095/)

`{24/[2]/[4]/(3)/(3)/(1)/(1)} · {{i}} · .dlw`
