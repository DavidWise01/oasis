# AETHER-140 — Physical uncertainty and coverage requirements

**Phase VIII 4/8 · 50% software readiness; 0% empirical physical validation.**

The **local** synthetic experiment passed 5,120 of 5,120 acceptance checks across 320 episodes per policy (40 seeds, eight scenarios, 24 ticks per episode).

Signed-only authorization falsely permitted **1,920 unsafe dry-run ACT** in six constructed uncertainty/certificate failures, compared with **zero** for the bounded-uncertainty gate. Both policies retained **5,760 safe dry-run ACT** (960 clean and 960 valid-rotation), while **every operational ACT remains HOLD**.

The six fault conditions are missing uncertainty budget, unsupported confidence/coverage claim, common calibration ancestry treated as independent, upper interval crossing the threshold, expired uncertainty certificate, and negative/understated uncertainty. Failures are rejected, not repaired.

**Deliberately conservative model:** A bounded risk uses a mock reference value plus explicitly declared worst-case random, reference, shared-source and systematic error envelopes. With illustrated terms 0.001, 0.001, 0.002, 0.003, upper risk is reference value + **0.007**; when that exceeds permission limit 0.025, HOLD. These are asserted bounds, **not statistically established intervals or laboratory-measured tolerances**. The source ancestry is also an assumption.

No physical sensor or independent calibrated reference was connected. Software can enforce a claimed confidence budget but cannot demonstrate its empirical coverage, source independence or accuracy. The physical acceptance counter stays **0%** and no real actions are authorized.

**Source reproducibility caveat:** The local executed source SHA-256 is `9e2e5260c2f7fe62405b14f2fd617a4e9cf9e171387352e36e8475efd2959dcf`. This GitHub repository includes a **separately authored checkout-oriented `experiment.py`**, not byte-identical to the locally executed code; numerical GitHub-checkout replay is not independently verified. The summarized `results.csv` and `manifest.json` document the local run. The full local source, checks, seed summary and traces are in the downloadable evidence ZIP.

[Python experiment](experiment.py) · [Local results](results.csv) · [Local acceptance manifest](manifest.json) · [Interactive Pages laboratory](index.html) · [Phase VIII tracker](../PHASE-VIII-STATUS.md).
