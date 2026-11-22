# AETHER-102 — Homeostasis Under Unseen Dynamics

**Phase II Turn 7: FAILED acceptance; completion stays 6/8 = 75%.**

The AETHER-101 governing policy was imported **unchanged** from `../101/experiment.py` and evaluated on fresh seeds 102001–102060 in five unseen synthetic regimes. Each case contains 96 inspections; 300 paired cases × 96 = **28,800 inspected ticks per policy**.

## Stressors

1. `flash_shift`: brief severe hazard, followed by another later episode.
2. `scarce_audit`: observation budget falls from 140 to 28 samples during a shift.
3. `phase_chirp`: time-varying oscillation frequency.
4. `guard_degradation`: guarding's multiplier rises from 0.55× baseline risk to **1.35× risk** during part of the episode, violating the assumed protective effect.
5. `correlated_audit`: temporally correlated common-mode bias contaminates audit observations.

All five use synthetic independently seeded data. True risks and guard effectiveness are **evaluation truth**, not live features available to the controller.

## Results

| Environment | Direct cost | Frozen selector cost | Selector minus direct |
|---|---:|---:|---:|
| Flash shift | 43,397.5 | 42,959.7 | −437.8 |
| Scarce audit | 44,544.5 | 44,022.5 | −522.0 |
| Phase chirp | 52,982.5 | 50,806.7 | −2,175.8 |
| **Guard degradation** | **49,593.5** | **50,036.7** | **+443.2** |
| Correlated audit | 54,265.0 | 51,006.6 | −3,258.4 |
| **All** | **244,783.0** | **238,832.2** | **−5,950.8** |

Aggregate wrong action outcomes fall **7,719 → 7,098**; unsafe authorized ticks remain **236 → 236**. Guarded actions occur 432 times under the selector, versus zero in the baseline. Both HOLD counts are 15,770.

## Acceptance

- Frozen replay, prefix, hash chain and admissibility checks: **300/300 in each category** — PASS.
- No more unsafe authorized ticks: **236 vs 236** — PASS.
- No increase in overall cost: **−5,950.8** — PASS.
- No increase in **any** individual regime: **+443.2 for guard degradation** — FAIL.

**Overall: FAILED.** A globally beneficial result cannot overwrite a local failure. No phase credit awarded.

The test's causal-prefix check is a deterministic repeat of an identical prefix, not a new future-data perturbation test; the strong independent future-perturbation test was performed in AETHER-101. A Clopper–Pearson bound computed on past audit measurements does not guarantee present risk under correlated observations or structural drift.

## Reproduction

`python aether/102/experiment.py` with NumPy and SciPy installed. The script imports the frozen AETHER-101 selector and regenerates `seed_results.csv`, `results.csv`, `trace_samples.csv`, and `manifest.json`.

## Next natural bound

**AETHER-102B — Guard-Effectiveness Drift Gate.** Identify when the guarded-action benefit no longer holds, without exposing hidden simulator effectiveness, and conservatively revert to direct or HOLD. Freeze a selection criterion on development data and evaluate on new seeds. Do not advance Phase II until the safety and per-regime economic gates pass.

[Pages lab](https://davidwise01.github.io/oasis/aether/102/) · [Phase II status](../PHASE-II-STATUS.md)

`{24/[2]/[4]/(3)/(3)/(1)/(1)} · {{i}} · .dlw`
