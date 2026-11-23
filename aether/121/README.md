# AETHER-121 — Measurement Integrity, Phase VI

**PASS — bounded synthetic acceptance.** Eight regimes × 60 seeds = 480 paired episodes; 24 inspections each; 11,520 actions per policy. All 5,760 replay, hash-chain, signed-packet, calibration fail-closed, zero-unsafe and causal-time checks passed.

**Problem:** a correctly signed packet can contain biased sensor readings. **Correction:** current signed readings of two controller-provided known challenge patterns (8 and 100 error bits in a 560-bit test) must match the reference values within ±1 before the risk report may authorize ACT. Else HOLD.

**Results:** signed-only **1,118 unsafe authorizations** vs calibrated **0** under the synthetic sensor biases; **840/840** safe ACT preserved in clean conditions and **539/539** in the risk-transition condition. Across all regimes safe ACT fell from **5,578 to 2,938**, highlighting the cost to availability when sensors fail. Illustrative cost: 760,950.4 vs 418,678.4 units, not a real-world estimate.

Scenario families: clean, negative additive bias, gradual drift, stuck-low output, abrupt bias, positive bias, calibration fault, risk transitions. Each episode is deterministic from seed and scenario; signatures use a synthetic HMAC key. Run `python experiment.py` with NumPy and SciPy to generate the full trace and six-check audit.

**Assumptions and limits:** The challenge source and scheduling are trusted; the sensor is assumed not to selectively falsify only ordinary risk readings while accurately answering known challenges. A sophisticated signed falsehood can pass. Source independence, protected counters, and signing keys are not verified by this simulation. No witness/quorum model; one controller. Phase V remains frozen at 100%.

[Results](results.csv) · [Manifest](manifest.json) · [Interactive laboratory](index.html).
