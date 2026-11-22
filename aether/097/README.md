# AETHER-097 — Context Contradictions and Revocation

**Phase II / Turn 2: PASS under the narrow synthetic acceptance gate. 2/8 = 25%.**

## Goal
A previously earned burst-context permission must be withdrawn when fresh observational evidence contradicts it. A single hegemonic governing risk rule chooses ACT or HOLD, with context affecting only whether an additional sentinel is purchased. The hidden regime flag is used **only** for generating data and evaluating performance; never for live policy decisions.

## Frozen rule and independent evaluation
Initial diagnostic threshold exploration used seeds 97001–97080. The fixed final burst signal was **current audit error count ≥7 OR two consecutive audit counts sum ≥13**. The contradiction controller revokes stored burst context on an audit count ≤3. Sticky comparator requires eight successive quiet audits. Immediate comparator has no retained permission.

The final untouched synthetic evaluation used 80 new seeds (97201–97280), two changing-environment scenarios, 100 ticks per trial, and three paired policies. All policies observe the same generated audit, sentinel, and held-out action outcomes. There are 140 audit roots and up to 80 sentinel roots per inspection, plus 150 independent action outcomes.

## Held-out results, pooled over 16,000 ticks per controller

| Policy | False context permission | Burst recall | Sentinel probes | Total cost |
|---|---:|---:|---:|---:|
| Sticky | 16.830% | 99.583% | 845 | 124,561.0 |
| Instantaneous | 0.777% | 98.208% | 357 | 124,185.6 |
| **Contradiction** | **0.786%** | **99.396%** | **362** | **124,189.6** |

Contradiction versus sticky: 371.4 units lower total cost, false context permission down by 16.044 percentage points. All tested post-burst transitions revoke within 0–1 inspection after the known transition, compared with 8-inspection censoring in the sticky comparator's eight-tick measurement window.

**Acceptance:** ≤1% false context permissions; fewer than sticky; no greater total cost than sticky. All passed. The immediate policy is marginally cheaper, so this does not claim universal superiority or optimality of the contradiction policy.

Cost = 10 × wrong authorized action + 0.05 × withheld action + 0.01 × observed label. Wrong authorized actions: 4,573 for sticky versus 4,576 for contradiction. Reduced stale permission, not reduced action error, drives the result.

## Files
- `experiment.py`: reproducible NumPy/SciPy simulator.
- `results.csv`: six scenario-policy rows plus pooled comparisons.
- `tick_audit.csv`, `counterexamples.csv`, `manifest.json`: generated when the script runs. The counterexample ledger preserves the first eight audit observations and revocation delay after each known burst exit.

## Limits
This is a small, stationary-form synthetic test with imposed known change points. Parameter selection occurred on earlier diagnostic seeds and the reported final seeds were untouched. No real-world confidence guarantee; no classification against all possible environmental forms. Within-tick audit is observed before the action, and delay is measured in subsequent inspection indices. AETHER-098 must ensure the directional and deterministic decision path cannot leak later evidence into an earlier authorization.

[Interactive Pages report](https://davidwise01.github.io/oasis/aether/097/) · [Phase tracker](../PHASE-II-STATUS.md) · [Previous AETHER-096B](../096b/)

**Next AETHER-098 — Deterministic Diodic Decision Path.**

`{24/[2]/[4]/(3)/(3)/(1)/(1)} · {{i}} · .dlw`
