# KET E.V.E. Experiment 32 — Decay-mode audit

Executed 2026-10-23 on the previous v31 13-nuclide held-out prediction CSV. Nuclear accounting A=Z+N passed for all 13 cases. Outcome grouped by observed dominant decay mode: stable/no observed decay: 7 cases, all classified long-lived; beta-minus: 5 cases, all short-lived (<1 year); double-beta-minus: 1 case, long-lived. Consequently every group lacks enough class variability for a meaningful within-mode lifetime classifier and no reliable shell-gap added-value estimate is possible.

## Exact result
- PASS: 13/13 nuclear bookkeeping checks.
- PASS: 3 categories, 7 stable, 5 beta-minus, 1 double-beta-minus.
- INCONCLUSIVE: within-decay-class stability predictive value because no group contains both label outcomes.
- BLOCKED: full bulk isotope download from external source in isolated Python container.
- NOT RUN: large-data isotope lifetime prediction.

Local reproducible package (supplied in conversation): `KET_EVE_32_Decay_Mode_Audit.zip` including `eve32.py`, `audit.json`, `decay_mode_audit.csv`, previous 13-row input, and README. Its optional `--input` supports downloaded IAEA LiveChart ground-state CSV and exports validated isotope records; **it does not fit a model**. Source https://iaea-nds.github.io/lc_api_notebook/ . Additional data references: https://amdc.impcas.ac.cn/web/masseval.html and https://amdc.impcas.ac.cn/web/nubase_en.html .

Next legitimate quantitative target: acquire broad evaluated isotope samples, separate observed decay modes, pre-register held-out element chains, calculate shell gaps from mass values, benchmark calibration and out-of-chain accuracy against composition-only baselines, and treat unobserved/stable half-life as censored. KET `[stable{(test-zone)}]` preserves failed or inconclusive results separately from structural shell-closure passes. Frozen 184/257 unchanged.