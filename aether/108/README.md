# AETHER-108 — Sparse-Sensor Resilience

**Phase IV · Turn 4/8 · ACCEPTED in synthetic tests · 50%.**

The governing controller remains singular and deterministic. The data path is diodic: observations collected or delivered after a decision cannot authorize an earlier action. Current-tick independent roots may be acquired as needed; duplicates and earlier-tick measurements never count as fresh evidence.

## Tested technique

AETHER-107 used an alpha-spending schedule α(t) = 0.05/[(t+1)(t+2)], for 24 inspections, with one-sided Clopper–Pearson independent-root upper bounds and a 2.5% authorization limit. AETHER-108 compares two acquisition methods under that same decision gate.

- **All-available:** acquire every distinct currently available root and decide.
- **Early impossibility:** acquire up to 280 roots; calculate the smallest upper bound obtainable if every remaining root had zero errors. If even this optimistic continuation could not justify ACT, choose HOLD immediately. Otherwise acquire the remaining roots and make the identical all-available decision.

Hidden actual-risk flags are evaluator-only. No source-root multiplicity is inferred: known grouping metadata is assumed accurate.

## Executed evaluation

120 seeds (108001–108120) × five environments × 24 ticks = **14,400 paired decision opportunities per policy**.

| Environment | ACT / 2880 | All-acquired roots | Economical roots | Savings |
|---|---:|---:|---:|---:|
| Full sensing | 1505 | 1,612,800 | 1,273,160 | 339,640 |
| Half missing | 450 | 806,400 | 806,400 | 0 |
| Half delayed | 447 | 806,400 | 806,400 | 0 |
| Tenfold correlated | 0 | 161,280 | 161,280 | 0 |
| Hazard and intermittent scarcity | 1087 | 1,344,000 | 1,100,960 | 243,040 |
| **ALL** | **3489** | **4,730,880** | **4,148,200** | **582,680** |

Both policies issued exactly the same 3,489 ACT and 10,911 HOLD decisions, with 0 unsafe authorized inspection ticks in the 14,400 paired cases. The economical policy reduced acquired independent roots by **12.316%**, and illustrative total cost from **144,211.3 to 138,384.5**, a saving of **5,826.8**. The total confidence error allowance is 0.048 across the 24 looks.

The delayed environment excluded 772,800 stale reports per policy; the correlated setting excluded 1,451,520 repeated reports per policy. The simulator constructs the sources and timestamps explicitly. Identical decisions follow from the monotonic upper-bound property, not from a learned classifier.

## Gate and limitations

Gate: **zero decision mismatches, no added unsafe authorizations, total cost below all-available and at least 1,000 safe/full-regime ACT decisions.** All four passed.

In the tenfold-correlated condition, only 56 true roots were available per tick. The controller issued **0 ACT** decisions; this is an appropriate limitation of unsupported evidence, not demonstrated graceful throughput. When data cannot certify safety, HOLD.

This synthetic demonstration assumes known source ancestry, independent Bernoulli roots within each tick, accurate timestamps and a fixed 24-look horizon. The same confidence control does not automatically apply to unknown dependency or arbitrary time horizons.

### Run

`python aether/108/experiment.py` (NumPy and SciPy). Regenerates `seed_results.csv`, `results.csv`, `trace_samples.csv` and `manifest.json`.

[Interactive Pages lab](https://davidwise01.github.io/oasis/aether/108/) · [Phase tracker](../PHASE-IV-STATUS.md) · [AETHER-107](../107/)

**Next natural bound — AETHER-109: recovery when sensing resumes.** Require fresh eligible roots to reopen useful ACT decisions after a temporary outage, without using stale receipts.

`{24/[2]/[4]/(3)/(3)/(1)/(1)} · {{i}} · .dlw`
