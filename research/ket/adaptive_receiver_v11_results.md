# KET Experiment 11 — Adaptive receiver under drifting noise

Numerical simulation only. Local executable: `adaptive_receiver_v11.py` (provided as conversation artifact).

## Structure and assumptions
- 16 sensing nodes: 2 grandmothers, 2 mothers, 4 daughters, 8 granddaughters, plus one dark reference channel.
- Modulated input at 73 Hz; 512 Hz sample rate; 1024 samples per trial.
- Signal amplitude: 0.075 arbitrary units, nodes scale with `0.85 ** generation`.
- Four epochs with shared-noise SD: 0.12, 0.55, 1.15, 0.30.
- 100 detection trials, 100 null holdout trials, and 100 independent null threshold-calibration trials for each method and epoch.
- Methods: ordinary averaging, covariance-derived weights fixed from first epoch, covariance-derived weights recalibrated from 3 sec dark samples per epoch.
- Every method receives a separately calibrated 99th-percentile null threshold for each epoch (this is a controlled comparison of *spatial weights*, not a test of frozen thresholds).
- Synthetic Gaussian noise; per-node independent SD 0.48; dark-reference independent SD 0.336; covariance ridge regularization.

## Results (locks /100; false alarms /100)
| Shared noise | Method | Correct locks | False alarms |
|---|---|---:|---:|
| 0.12 | Average | 99 | 1 |
| 0.12 | Fixed weights | 99 | 0 |
| 0.12 | Adaptive weights | 100 | 3 |
| 0.55 | Average | 4 | 4 |
| 0.55 | Fixed weights | 9 | 2 |
| 0.55 | Adaptive weights | 51 | 3 |
| 1.15 | Average | 0 | 4 |
| 1.15 | Fixed weights | 0 | 0 |
| 1.15 | Adaptive weights | 45 | 2 |
| 0.30 | Average | 39 | 4 |
| 0.30 | Fixed weights | 60 | 5 |
| 0.30 | Adaptive weights | 86 | 3 |

Local validation: PASS for 2:2:4:8 node counts, noise-only null calibration, blind frequency peak detection, signal/no-signal holdout, false alarm sanity checks.

## Cautions
- This is a statistical optical/electrical readout surrogate, not experimental proof of toroidal geometry, cryogenic behavior, direct pixel RF sensing, or any hardware reception.
- Recalibration uses idealized signal-free dark samples and modeled noise behavior; online self-calibration during reception is not yet tested.
- No physical capacitance calibration or electromagnetic field solver in this run.
- Frozen 184/257 ancestry unchanged.
