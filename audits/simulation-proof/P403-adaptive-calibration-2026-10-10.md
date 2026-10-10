# P4.03 fixed versus adaptive clock calibration

Executed locally with Node.js v22.16.0. 121 cycles x 200 layers = 24,200 views *per policy*. Regression: **251/251 assertions PASS**; wall duration ~361.35 ms for the benchmark/test run.

| Policy | Accepted | Quarantined | Simulated late |
|---|---:|---:|---:|
| Fixed zero correction | 11,556 | 12,628 | 16 |
| Adaptive running correction | 23,424 | 760 | 16 |

Adaptive quarantine reduction: (12628 - 760) / 12628 = 93.98%. Test uses deterministic slowly varying seven-clock offsets up to 0.5 ms, bounded synthetic measurement noise, 0.25 ms acceptance bound, and the same injected missed deadlines. This is not a fair comparison against an optimally calibrated fixed-rate controller, and is not real-world performance evidence. Adaptive measurements are used for the current cycle and assumed trusted. No wall-clock realtime guarantee, external witness durability, or physical quantum/decoherence claim. Exact BigInt 10^-36s register and 200-layer/200ms conceptual clock retained.

P4.03 runnable source, prior dependencies, regression and raw results are in the chat ZIP; they are not part of this audit commit.