# AETHER-101 — Deterministic Best-Admissible Action Selection

**Phase II Turn 6: ACCEPTED (synthetic) — 6/8 = 75%.**

## Governing rule
One canonical controller chooses exactly one action per tick: DIRECT, GUARDED, or HOLD. Both active actions face the **same** one-sided 95% fixed-time Clopper–Pearson upper-risk admissibility constraint of ≤2% using current and up to four preceding audit batches. If neither active action passes, HOLD is required. Among admissible active choices, rank first by observable harm class, then direct cost, then observation cost, then stable action identifier. Under an observed stress marker (≥3 audit errors in the current 140-sample batch) GUARDED has a lower harm class; otherwise DIRECT is the cheaper selection.

**No choice** means deterministic resolution, not a license to ignore evidence or force an inadmissible action.

## Executed evaluation
80 seeds per scenario (101001–101080) across stable, abrupt and oscillatory synthetic Bernoulli risks. 96 ticks per seed; 23,040 evaluated actions. Each tick gets 140 observed audit samples and 150 independent held-out action outcomes. The model assumes the GUARDED action reduces the error probability by **45%**, which is an explicit simulation premise, not an empirical real-world property.

The initial development design incorrectly allowed GUARDED to pass a softer risk gate. It caused dramatically more wrong actions and cost; it was rejected and revised before the accepted run. The accepted design shares the same hard admissibility rule for both active actions.

## Evidence

| Metric | Direct-only baseline | Best-admissible selector |
|---|---:|---:|
| DIRECT | 16,580 | 16,304 |
| GUARDED | 0 | 276 |
| HOLD | 6,460 | 6,460 |
| Wrong authorized outcomes | 8,733 | 8,317 |
| Unsafe authorized ticks | 137 | 137 |
| Total illustrative cost | 184,616.0 | **180,621.6** |

Observed cost improvement: **3,994.4 (2.16%)** without extra risk-gate authorizations.

Five test categories each pass 240/240 episodes: replay determinism, future-data prefix invariance, option-order invariance, hash-chain recomputation, exact action-choice verification. Additional fallback and tie-breaking checks pass.

Cost assumes 10 per wrong authorized outcome, .05 per withheld action, .01 per audit sample, 1.0 per DIRECT action and 1.6 per GUARDED action.

## Reproduce
Run `python aether/101/experiment.py` using Python, NumPy and SciPy. It writes `seed_results.csv`, `results.csv`, `trace_samples.csv` and `manifest.json`.

**Limits:** Historic risk estimates do not ensure instantaneous safety under change. No model-free or production guarantee is implied. The selected policy is best under the explicitly coded priority and assumptions, not universally optimal.

[Pages-ready lab](https://davidwise01.github.io/oasis/aether/101/) · [Phase tracker](../PHASE-II-STATUS.md) · [Previous 100B](../100b/)

**Next — AETHER-102:** homeostatic stress under unseen environmental dynamics, scarce evidence, changing risk, actuator mismatch and previously unmodeled disturbances. Do not open a witness/quorum or Byzantine branch during this phase.

`{24/[2]/[4]/(3)/(3)/(1)/(1)} · {{i}} · .dlw`
