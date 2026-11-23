# AETHER-112 — Phase IV Closure and Integration

**Phase IV CLOSED at 8/8 = 100%**, subject to the bounded synthetic acceptance contract.

## What was tested

The frozen single-controller AETHER-111B implementation was replayed across **120 new integration cases** (5 scenarios × 12 new seeds × 2 controllers), totaling **2,880** decisions. Six checks per case:

1. Identical inputs yield identical output traces and hashes (120/120)
2. Mutating ticks 13–24 cannot alter the first 12 outputs (120/120)
3. Every append-only SHA-256 trace-link recomputes (120/120)
4. Missing / unverifiable packets always HOLD (120/120)
5. All ACT decisions require valid packets and computed admissible bound (120/120)
6. Resource budgets never go negative or overspend (120/120)

**Total: 720 / 720 passed.** The controller issued **1,132 ACT** and **1,748 HOLD**, with **0 observed unsafe-authorized ticks** in this sampled synthetic run.

## Archive preservation

The source inventory records SHA-256 digests, lengths and names for the `experiment.py`, `results.csv` and `manifest.json` files of seven accepted predecessor bounds: **105, 106, 107, 108, 109b, 110, 111b**. It also records the failed **109** and **111** bounds rather than erasing or overwriting their evidence. This is **27 archived files**. The integrated 111B controller was actually reexecuted; the older bounds were only checked for file existence and checksums, **not rerun in this closure**.

## Governing constraints

One hegemonic controller, diodic/forward-only observation and append-only evidence. No evidence from the future informs past actions. Missing or uncertified observations fail closed. When no action is supported, `HOLD`.

No witness quorum, Byzantine agreement or distributed authority is implemented in this phase. The hard boundary was honored.

## Scientific limits

The ingress layer's claim that packets are valid and roots independent is an **assumption**, not a fact established by the model. The probability bounds are fixed-time binomial constructions and do not universally guarantee safety under drift, adversarial streams or unseen distributions. 0 unsafe ticks in 2,880 simulated decisions is a sample result, not a general zero-risk bound.

## Files and reproducibility

- `experiment.py`: closure integration runner
- `integration_cases.csv`: per-case checks, actions, cost and outcome counts
- `inventory.csv`: checksums for accepted and preserved failed-bound artifacts
- `manifest.json`: final closure summary
- `index.html`: interactive lab and phase-summary page

Run the integration script against a directory that contains the archived `aether105`, `aether106`, etc. directories and NumPy/SciPy installed:

```bash
python aether/112/experiment.py --source-root /mnt/data
```

**Status:** Phase IV closed at 100%; separate Phase V must start at 0% with independently defined scope and acceptance criteria.

[GitHub Pages closure lab](https://davidwise01.github.io/oasis/aether/112/) · [Phase IV tracker](../PHASE-IV-STATUS.md) · [Previous corrected stress test](../111b/)

`{24/[2]/[4]/(3)/(3)/(1)/(1)} · {{i}} · .dlw`
