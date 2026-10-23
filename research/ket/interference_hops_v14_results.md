# KET experiment 14 — competing modulation and sudden frequency hops

Run date: 2026-10-23. Synthetic electrical-readout experiment, locally executed with NumPy. Full executable and JSON results attached to the conversation.

## Model
- 16 sensing nodes across 2 grandmothers / 2 mothers / 4 daughters / 8 granddaughters, plus one dark reference.
- 512 samples/s, 1024 samples per block; 80 trials, 12 blocks per trial.
- Target: initially random 42–90 Hz, jumps +15 Hz at block 4 and −23 Hz at block 8.
- Competitor: random 108–144 Hz; stronger than the target in the basic per-channel waveform model.
- Target spatial response scales as 0.85^generation; competitor alternates between 1.0 and 0.35 across channels.
- Shared Gaussian noise and independent Gaussian node noise.
- Blind frequency search 25–160 Hz; lock threshold spectral peak/median ≥6.
- Baseline is equal averaging. Spatial receiver constrains a known target response to unity and nulls a **known** interferer response plus common mode.
- Target modulation AC amplitude 0.35, competitor AC amplitude 0.40. Spatial receiver knows the two signal vectors, not frequencies.

## Observed results (correct target locks/960)
| Condition | Averaging | Spatially selective |
|---|---:|---:|
| Target only | 437 | 888 |
| Target + competitor | 282 | 905 |
| Target + competitor + frequency hops | 244 | 897 |

Immediate post-hop correct locks: 27/160 averaging vs 154/160 spatial.
Noise-only null: 0/960 false locks for each.
Competitor-only null: 612/960 locks onto competitor for averaging vs 0/960 for spatial.
All above figures are finite Monte Carlo sample results, not universal probability bounds.

## Interpretation and limitations
The calculation demonstrates how prior knowledge of different multi-node electrical response patterns can reject a stronger interferer while retaining target sensitivity and following abrupt modulation-frequency changes. It does not show autonomous unknown-interferer rejection, real optical hardware, RF reception, toroidal electromagnetic modes, cryogenic sensor performance, or any novel physical interaction.

Next target: estimate the competitor's spatial signature from observations rather than giving it to the receiver, then measure convergence and failure conditions.
Frozen 184/257 reference unchanged.
