# AETHER-149 — Measured same-path challenge protocol readiness

**Phase IX Turn 5/8 · locally tested synthetic protocol PASS · readiness 62.5% · physical qualification 0%.**

The full local test exercised 30 seeds × eight cases × 20 decision ticks = **240 episodes and 4,800 decisions per policy**, with **3,840/3,840 deterministic checks passed**. Signed-only acceptance admitted **1,440 unsafe dry-run ACT**. Same-path challenge gating admitted **0 unsafe dry-run ACT** and kept **3,360 safe dry-run ACT** including 600 clean and 600 valid replacement/rotation actions.

Six fault conditions are challenged: missing calibration pulse, bypassed calibration probe, substituted operation route, reused challenge counter, excessive timing separation, and false path assertion. The constructed pulse response, device generation, counter, challenge nonce, ingress path and time window must all agree before a synthetic dry-run action can be admitted. The original evidence ledger is SHA-256 chained and no source observations are silently rewritten.

**Physical limit**: The simulated bench already knows risk and route truth, and can produce perfectly consistent signed responses. No physical probe was inserted into actual hardware. This software test does not establish that a sensor and challenge occupy the same real physical path. **All operational ACT remain HOLD; empirical physical qualification stays at 0%.**

The complete locally executed Python source SHA-256 is `dd0c2084db331273789b29a03a0b98285f01db540ef2f38555c6d8d5e57f8ddf`. The GitHub `experiment.py` is a separately authored reduced reproducer, not byte-identical to the local test. Independent checkout execution and live Pages deployment are not verified. Full 3,840 checks, seed results, traces, manifest and exact source are in the ZIP attachment.

[Standalone demonstration](experiment.py) · [Local results](results.csv) · [Manifest](manifest.json) · [Interactive lab](index.html) · [Phase IX tracker](../PHASE-IX-STATUS.md).
