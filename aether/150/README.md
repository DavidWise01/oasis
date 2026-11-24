# AETHER-150 — Drift and Alarm Characterization Protocol

**Phase IX Turn 6/8 · Local synthetic software readiness PASS · 75% software / 0% physical.**

The full locally executed test ran 30 seeds × eight cases × 20 ticks, **240 paired episodes and 4,800 decisions per policy**. All **3,840/3,840** replay, append-only SHA-256 evidence-chain, temporal-order, single-action, modeled-safety, fail-closed, clean/replacement-availability and operational HOLD tests passed.

Under **signed-only** admission, **1,440 unsafe dry-run ACT** occurred across six constructed failure regimes: hidden slow drift, abrupt drift, suppressed alarms, delayed alarms, stale calibration and forged drift certificates. The **drift/alarm-gated** policy allowed **zero unsafe dry-run ACT** while preserving **3,360 safe dry-run ACT**, including 600/600 clean and 600/600 valid-replacement actions.

The controller's synthetic gate requires bound device identity, generation, nonce, tick and counter; current calibration epoch/expiry; external reference identity; independent modeled alarm state; bounded alarm delay, uncertainty and drift budget; and an upper risk below the permission threshold. Failures generate HOLD and do not rewrite source data.

**No physical qualification was performed.** The reference oracle has direct access to simulated truth, and cryptographic roots are software HMAC fixtures. This test establishes no empirically measured drift rate, detection probability, alarm latency, calibration trust or physical acquisition path. Every operational action remains HOLD.

Local executed source SHA-256: `b6459d27a9f15b7d29a6410e178c44dae365268cd524a6393084d711523c75e1`. The GitHub `experiment.py` is a separately authored reduced reproducibility demonstration, not the byte-identical local program. Independent GitHub-checkout replay and live Pages deployment are unverified. Full executed code, local results, seed reports, 3,840 checks, manifest, and sample SHA-256 chains are in the accompanying ZIP.

[Python demonstration](experiment.py) · [Local aggregate results](results.csv) · [Manifest](manifest.json) · [Interactive laboratory](index.html) · [Phase IX tracker](../PHASE-IX-STATUS.md).
