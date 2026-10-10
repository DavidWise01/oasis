# P4.04 — calibrated fixed-rate vs adaptive controller (2026-10-10)

Executed locally on Node.js 22, using the P4.02/P4.03 kernels and exact BigInt time register (1e-36 s). 121 simulated cycles × 200 views × 3 scenarios per policy = 72,600 views per policy. Regression PASS: 31 assertions. Benchmark wall time approximately 791.53 ms (one local run).

| Scenario | Fixed accepted / quarantined / late | Adaptive accepted / quarantined / late |
|---|---|---|
| Smooth drift | 24184 / 0 / 16 | 24184 / 0 / 16 |
| Abrupt step change | 23784 / 400 / 16 | 23984 / 200 / 16 |
| Forged sensor measurements | 22388 / 1796 / 16 | 22388 / 1796 / 16 |

**Important result:** Adaptive correction reduced quarantine under the abrupt step by 50% but gave no benefit under forged measurements. Authentic HMAC protection does not establish physical measurement truth: a false offset can be signed with an authorized key. In the simulation the gate uses the known true offset, so its reported false-accept count of 0 is a reference-oracle property, not a realistic independently verified detection guarantee.

The tested fixed-rate controller extrapolates recent measurements rather than using P4.03's zero-correction baseline. Missed deadlines are injected, not actual OS timer samples. No non-rollbackable independent +1 witness or live clock calibration in this prototype. Symbolic architecture preserved: 200 layers/200ms, 7 OSI bands per 100 layers, 60-point DIATOM, blockade `{-{+{%}+}-}`.

Runnable benchmark, 31-assertion test and dependencies in the P4.04 downloadable ZIP.