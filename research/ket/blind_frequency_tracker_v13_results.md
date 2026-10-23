# KET Experiment 13 — Blind frequency discovery and tracking

Date: 2026-10-23. Synthetic numerical experiment; **not RF reception or measured cryogenic hardware**.

## Model
2 grandmothers, 2 mothers, 4 daughters, 8 granddaughters (16 channels) plus one dark reference. Receiver searches 25–160 Hz without advance knowledge of signal frequency, starting signal randomly between 40–100 Hz with random step drift of up to ±0.32 Hz per 4-second block. Sample rate 512 Hz; 2048 samples per block (0.25 Hz FFT bin resolution). Acquisition scans entire band; lock tracking searches within ±2.5 Hz of prior lock, with peak-to-median-noise ratio threshold 6. Known node response vector is used to form common-mode-rejecting weights. Simulation includes 4% per-channel common-noise coupling mismatch drawn each block. Independent channel noise is simulated as Gaussian. Reproducible local code provided separately in conversation as `blind_tracker_v13.py`.

## Holdout results
80 present trials × 12 blocks = 960 present blocks per condition; 80 independent absent trials × 12 blocks = 960 null blocks per condition.

| Shared-noise SD | Correct/960 | Correct % | False locks/960 |
|---|---:|---:|---:|
| 0.4 | 854 | 88.96% | 0 |
| 1.2 | 851 | 88.65% | 0 |
| 2.5 | 819 | 85.31% | 0 |

A correct hit requires a detected lock within 0.5 Hz of the injected signal frequency. No false locks were observed in 2880 null blocks (not a guarantee of zero population false-alarm probability).

## Caveats and next falsification
The model is optical modulation plus electrical readout noise, **not** RF scanning by a screen pixel. It retains prior knowledge of a bounded modulation search range and 16-channel amplitude signature. Noise is Gaussian; unmodeled nonlinearities, interferers, multiple concurrent transmitters, blind spatial-profile learning, sudden frequency hops, and hardware/capacitive geometry are not covered. Next: test competing signals, abrupt frequency hops, and incorrect geometry assumptions.

Frozen 184/257 ancestry unchanged.
