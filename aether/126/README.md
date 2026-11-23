# AETHER-126 — Adaptive Calibration Resource Economics

**Synthetic acceptance passed.** Run `python experiment.py` with NumPy and SciPy to regenerate CSV output and the manifest. New seeds 126001–126060, seven environments, 32 ticks each: **420 paired episodes, 13,440 decisions per policy**, **5,880/5,880** reproducibility, hash integrity, one-action-per-tick, fail-closed, safety, probe-budget and new-generation checks.

**Policy:** Fixed buys four interior probes for each accepted packet. Adaptive buys four for its initial anchor, every fourth accepted inspection, after instrument-generation changes or noisy / suspicious readings; otherwise buys two same-path monitor probes, validates them against the recent full calibration with conservative drift allowance, and applies an extra error-count margin. No current valid risk packet means HOLD, regardless of calibration state.

| Controller | Calibration probes | Unsafe ACT | Safe ACT | Total synthetic cost |
|---|---:|---:|---:|---:|
| Fixed | 50,880 | 0 | 8,322 | 384,873.6 |
| Adaptive | 37,080 | 0 | 8,605 | 354,104.0 |

Savings: **13,800 probes (27.12%)**, **30,769.6 modeled cost (7.99%)**. Stable scenario preserved **1,917/1,917** safe ACT and reduced probes **7,680 to 4,800**. Scenario-dependent availability: noise burst 1,368→1,297, hazard step 1,380→1,379, broken calibration 1,439→1,438, missing certificate 1,200→1,197 safe ACT. Slow drift happened to improve safe ACT 240→599 in the bounded simulation; do not generalize.

**Limits:** Only tested synthetic risk sequences, an affine measurement response, trusted HMAC signer/counter, truthful noise metadata and assumed bounded drift between calibration anchors. An abrupt hidden drift step not detected by the two monitor probes can invalidate this result. Pointwise 95% Clopper-Pearson bounds do not imply an experiment-wide false-authorization rate. This is a cost/safety comparison under constructed assumptions, not field evidence.

**Phase VI:** Turn 6 accepted, 6/8 = **75%**. Phase V remains frozen.
