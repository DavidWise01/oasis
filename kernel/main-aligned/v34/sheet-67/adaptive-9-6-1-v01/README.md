# SHEET 67 — Adaptive 9/6/1 / sqrt(1.25) Homeostasis

Linear append-only successor to SHEET 66. User-specified notation: `9/6/1`, `sqrt1.25`. **Implementation interpretation:** 9 ingress cells → 6 relay queues → 1 shared root register. There is no claim this is the only possible interpretation of the notation.

At every simulation tick, a fixed budget of 36 operations is divided among 16 node queues. Fixed control uses equal allocation; adaptive uses backlog-weighted allocation whenever a node's queue depth exceeds `sqrt(1.25) * (36/16)`. This is a **real scheduling condition**, not a cosmetic label. A destination's physical/global clock is not changed.

## Locally executed test

| Workload | Scheduler | Accepted and delivered | Finish tick | Peak backlog | Mean wait |
|---|---|---:|---:|---:|---:|
| Balanced | Fixed | 3,456 | 1,729 | 3,244 | 812.0 |
| Balanced | Adaptive | 3,456 | 290 | 2,804 | 131.703 |
| Hotspot | Fixed | 3,456 | 1,729 | 3,244 | 812.0 |
| Hotspot | Adaptive | 3,456 | 290 | 2,790 | 130.831 |

9/9 checks passed after repairing a synthetic-hotspot generator that initially left out one cell and one regional relay (the first run was 7/9). Identity set preserved, zero accounting loss, and constant per-tick budget. Locally generated `benchmark.py` and `results.json` can be downloaded from the associated conversation. GitHub version is separately transcribed; independent CI replay remains pending.

**Limitations:** Fixed equal allocation wastes operations on empty nodes, explaining much of the gain. The model uses logical queue and SHA-256 commitments, *not* physical portals, real time dilation, or transformer attention head computations. No crash recovery or adversarial authentication here.
