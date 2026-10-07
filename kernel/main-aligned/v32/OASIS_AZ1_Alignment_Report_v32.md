# OASIS AZ1 Scientific-Civilization Alignment — v32

## Decision

**Keep. This is one of the stronger executable historical packages, but it contains version drift that needs to stay visible.**

The current `_tick.py` is a deterministic shared-research state machine. The uploaded `_simulate.py` matches that engine and passes. The uploaded `_physics.py` belongs to the previous idea-evolution engine and is no longer compatible.

## Current engine test

Uploaded `_simulate.py 200`:

- return code: **0**
- verdict: **9/9 PASS**
- event histogram: **{'research': 189, 'discovery': 3, 'setback': 8}**
- frontier monotone: **PASS**
- setbacks preserve frontier level: **PASS**
- deterministic rerun: **PASS**

## Chronicle replay

The uploaded chronicle has **86** retained entries and ends at:

- day 86
- level 2
- research 0.375
- knowledge 2.86
- era `the First Tools`

Replaying the current `run_research()` from a fresh state using the chronicle's own recorded dates reproduced **every retained entry exactly** and reproduced the final state exactly.

Result: **PASS**

This is stronger than merely checking the current JSON fields: the history is reproducible from the current transition function.

## Audit drift found

`_physics.py` exits **1** against the current `_tick.py`.

Failure:

`AttributeError: module '_tick' has no attribute 'CORP'`

It expects the old `CORP` / `run_epoch` idea-evolution API. Therefore the old Marie-Curie "5/5 laws hold" receipt is a legacy result, not a current regression certification.

Also, current `_tick.main()` writes the chronicle and performs git commit/push directly; it does not invoke `_physics.py` as a pre-commit gate.

## Long-horizon defect

The 200-day burn-in is good, but the invariant is horizon-sensitive.

With the harness start date 2026-06-29:

- first reaches final science-tree level 34: **day 11251 (2057-04-17)**
- first `research < threshold` violation: **day 11849 (2058-12-06)**
- research = **12.921**
- terminal threshold = **12.900**

Cause: once `level == len(TREE)-1`, the discovery branch can no longer fire and subtract the threshold, so research continues accumulating indefinitely.

I generated `AZ1_Current_Audit_v32.py`; it deliberately exits nonzero until that terminal policy is resolved.

Current diagnostic verdict:

```
[PASS] 200-day run
[PASS] frontier monotone
[PASS] deterministic
[PASS] uploaded chronicle exact replay
[FAIL] terminal research remains bounded
       first violation: day 11849 level 34 research 12.921 threshold 12.900
VERDICT: 4/5 passed
```

## Corpus evolution

Previous v31 snapshot: **859**
Current `az1-corpus.json`: **1321**

- retained: **854**
- added: **467**
- removed: **5**
- removed names: `AI-Audit-Tools, C-, Toph_Kernel, mainflux, root0`

Reconciliation:

- 854 + 5 = 859
- 854 + 467 = 1321

Therefore corpus *membership* is versioned, not append-only. OASIS provenance can remain append-only while each corpus snapshot records additions and removals.

Current corpus SHA-256, names joined by newline:

`809c45d96d368a94c7eded499b8dd825b69181a0415bebec1e78861891772879`

## Documentation drift

The uploaded README still describes the older **859-citizen cross-breeding idea-evolution simulation**. The current `_tick.py` and current index implement the later **scientific-civilization / shared science-tree** engine, while `az1-corpus.json` now contains **1321** names.

So README is archived as historical description rather than treated as the current executable spec.

## N-body visualization

The current HTML implements Sun-fixed pairwise Newtonian gravity with velocity-Verlet/leapfrog, and integrates **10 moving bodies**: nine planet labels including Pluto plus Halley.

Important reproducibility distinction:

- daily research engine: deterministic from `(date, day, state)`
- 3D N-body initial phases: **not deterministic across reloads** because the source seeds orbital mean anomaly with `Math.random()`

A fixed-seed Python reference implementation of the source integrator was run for 6,000 forward substeps and 6,000 reverse substeps:

- max relative energy deviation during forward run: **2.383e-07**
- max relative angular-momentum deviation: **2.665e-15**
- forward→reverse max position error: **2.533e-13 AU**
- forward→reverse max velocity error: **2.508e-12 AU/yr**

That supports the numerical reversibility of the velocity-Verlet algorithm under a fixed step sequence. It is not an exact replay of the page's random initial scene.

## Kernel result

Promoted to v32:

`deterministic research transition -> replayable chronicle -> versioned corpus receipt -> numerical N-body fixture`

Not promoted:

`historical audit label -> current authority`

All AZ1 support remains HOLD-only at the durable OASIS boundary.
