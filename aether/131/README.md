# AETHER-131 — Covariance-aware reference uncertainty

**Synthetic PASS**: eight scenarios × 50 seeded cases × 24 ticks = **400 paired episodes**, **9,600 decisions per policy**, **5,600/5,600 deterministic and evidence-chain checks**.

Signed-only independent-error combination ignored covariance. With two correlated reference contributions of ±0.004 in a risk observation near 0.018, assuming independence yields an illustrative upper risk of **0.02366**, under the **0.025** action threshold. With perfectly correlated common-source uncertainty, the modeled bound is **0.026**, requiring HOLD.

The independence comparator authorized **2,500 unsafe ACT** during the constructed shared-error and missing/stale-covariance scenarios. The covariance-aware policy authorized **0 unsafe ACT**, preserved **1,200/1,200** clean safe actions and **1,200/1,200** valid-rotation safe actions, and made **700 additional safe HOLDs** across all scenarios.

**The distinction:** Different signatures do not imply different physical calibration roots. Covariance must follow the source ancestry and uncertainty provenance. The controller fails closed when covariance data is missing, invalid or stale.

**Limitations:** This is an engineered synthetic falsification test, not a physical experiment or actual calibration trace. The rho coefficient, its uncertainty and causal source ancestry are assumed, not demonstrated. Combining one-standard-deviation components as a threshold is only an illustrative model and does not give a validated tail confidence or systematic worst-case bound. A real use case would require externally traceable covariance and a specified coverage probability. The local executable SHA-256 is `49fb21d19707e7dd6b02499563c8bbd184926fc1ffb3fe1ba6bcb448266ea654`; the published repository-compatible script was authored separately and is not claimed byte-identical until checkout replay.

[Experiment](experiment.py) · [Aggregate results](results.csv) · [Manifest](manifest.json) · [Interactive laboratory](index.html).

**Phase VII 2/8 → 3/8 = 37.5%.**
