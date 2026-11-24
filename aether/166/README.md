# AETHER-166 — Physical Drift and Alarm Evidence Intake

**Phase XI Turn 6/8 · 75% synthetic software readiness · 0% empirical physical qualification. Operational authority HOLD.**

The exact locally executed audit passed **3,200/3,200 checks** on 25 seeds × eight scenarios × 20 ticks, with **200 episodes / 4,000 decisions per policy**. Signed-only comparator admitted **1,200 unsafe synthetic dry-run ACT**. Drift/alarm gate admitted **0 unsafe** and preserved **2,800 safe synthetic dry-run ACT** (500 clean and 500 legitimate mock rotation). The policy was not passed seed, scenario or synthetic ground truth.

Six modeled faults: missing drift sample, excessive drift, suppressed alarm, delayed alarm, forged baseline epoch and clock regression. Synthetic software settings: drift limit .001 per tick, alarm deadline 50 ms, reference uncertainty .0005 and permission upper bound .025. This is a protocol contract, **not a physical measurement or qualified hardware tolerance**.

Real drift measurements, original acquisition files, calibrated clock, observed alarm latency and independent evidence are missing. [Physical alarm register](physical_alarm_register.json) retains explicit unknowns. No real-world permission is granted.

Exact executed source SHA-256: `5c096f560730de2171d5538c842bce3abfc52a7d452ca70db3b9db348cda9613`. Verified evidence ZIP SHA-256: `aea689f2ede7caa9a96bc454db0361a904f4050ae5d34dddcbb0e12039a2cca0`. Includes full source, check ledger, seed-level results and SHA-256 decision traces.

**Publication distinction:** GitHub `experiment.py` is a separate compact reproducer rather than the exact local audited source, and GitHub checkout replay is not verified. Live GitHub Pages deployment remains unverified.

[Python companion](experiment.py) · [Results](results.csv) · [Manifest](manifest.json) · [Physical evidence register](physical_alarm_register.json) · [Interactive lab](index.html) · [Phase XI tracker](../PHASE-XI-STATUS.md).

**Next bound AETHER-167:** blind adjudication of physical-evidence provenance and conflicts, with physical qualification 0% until genuine independent records exist.
