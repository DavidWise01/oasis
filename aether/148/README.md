# AETHER-148 — Empirical uncertainty and coverage acceptance protocol

**Phase IX 4/8, synthetic software readiness 50%, empirical physical qualification 0%.**

Local execution: 30 seeds × eight uncertainty conditions × 20 ticks = **240 episodes per policy**, **4,800 decisions per policy**, **3,840/3,840 deterministic checks passed**. Signed-only comparator made **1,440 unsafe dry-run ACT**, while the held-out-coverage gate made **zero**, retaining **3,360 safe dry-run ACT** including clean and legitimate-rotation cases **600/600** each. **All operational actions remain HOLD**.

A deterministic 120-sample held-out window is checked against a declared ±0.002 synthetic reference uncertainty envelope. The one-sided **90% Wilson lower bound must support at least 95% coverage** of the reference value. This is a software protocol rule, not an empirical certification of coverage. Samples are GENERATED from scenario truth, making their relationship to real sensor behavior wholly untested.

The six fault types are missing held-out samples, unsupported coverage claim, shared calibration ancestry, understated uncertainty, expired calibration, and reference upper interval crossing the action threshold (0.025). The gate fails closed without mutating previous receipts.

The locally executed full source SHA-256 is `17d1f3640c560ae636311ec73b0f01c146f61bc2a9274142bbb7ecfc73294b65`. The GitHub experiment.py is a separately authored smaller demonstration, not byte-identical to the local executable. Exact full local script, full checks, seed results and hash-chained traces accompany the evidence ZIP. GitHub checkout execution and live Pages deployment unverified.

**Physical qualification remains 0%:** no accredited physical reference, raw instrument measurement, acquisition-path verification or empirical calibration uncertainty has been validated.

[GitHub demo](experiment.py) · [Local aggregate results](results.csv) · [Manifest](manifest.json) · [Interactive lab](index.html) · [Phase tracker](../PHASE-IX-STATUS.md).
