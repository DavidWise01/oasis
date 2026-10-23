# Experiment 12 — Signal-protected online receiver adaptation

**Status:** PASS in local numerical simulation, 2026-10-23.

## Scope

Generational sensor topology: 2 grandmothers, 2 mothers, 4 daughters, 8 granddaughters, plus a dark reference channel. Target synthetic optical modulation 73 Hz. Each trial sampled at 512 Hz over 1024 samples. Sensor response modeled as 0.85^generation, amplitude 0.12; independent node noise SD 0.48; drifting common noise SD 0.12, 0.55, 1.15.

Three methods:
- **Ordinary average**: equal weighted sensing nodes.
- **Blind adaptation**: train noise covariance on live, potentially signal-contaminated data and choose minimum output-power weights with unit sum over sensing nodes.
- **Signal-protected adaptation**: regress out known 73 Hz sine/cosine basis in training blocks, fit covariance from residuals, and apply a constrained unity-response signal-space filter.

Training on alternating 128-sample blocks, and testing on disjoint alternating blocks. For each condition/method, 120 independent signal-absent threshold trials (99th percentile), 120 signal-present trials, and 120 independent signal-absent holdout trials. Synthetic data with fixed RNG seed 184257.

## Results

| Common-noise SD | Method | Signal hits / 120 | Null false alarms / 120 | Response w·S |
|---|---|---:|---:|---:|
| 0.12 | average | 120 | 6 | 0.719 |
| 0.12 | blind | 120 | 0 | 0.714 |
| 0.12 | protected | 120 | 3 | 1.000 |
| 0.55 | average | 62 | 4 | 0.719 |
| 0.55 | blind | 113 | 3 | 0.713 |
| 0.55 | protected | 118 | 0 | 1.000 |
| 1.15 | average | 8 | 1 | 0.719 |
| 1.15 | blind | 99 | 1 | 0.713 |
| 1.15 | protected | 107 | 1 | 1.000 |

Validated in local run: genealogy of 16 sensing nodes, held-out testing blocks, separately calibrated noise nulls, live-signal covariance estimates, and preserved constrained response.

**Limitations:** Target frequency and spatial signal response are known by protected detector. This is NOT blind autonomous frequency discovery, an electromagnetic field simulation, a toroidal antenna measurement, physical RF reception, or proof of cryogenic benefit. Noise-only threshold calibration still required for the controlled false-alarm comparison. The next experiment should hide the modulation frequency and track signals while both signal and noise drift.
