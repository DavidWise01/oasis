# Experiment 15 — Unknown-interferer spatial learning

Locally executed synthetic experiment. 16 channels: 2 GM, 2 MA, 4 DA, 8 GDA.

The learner knows the target generational amplitude template (0.85^generation) but is not supplied the interferer's spatial template. It examines spectral candidate bins, estimates a spatial nuisance template from a dissimilar peak, and projects away the estimated nuisance vector. Separate scenario: target only, target plus stronger competitor with hops, or competitor only. 80 trials times 12 blocks per scenario, 512 Hz sample rate, 1024 samples/block. Random target initial frequencies; hops +15 Hz at block 4 and -23 Hz at block 8. Interferer range 112–144 Hz; target start range 44–88 Hz. Seed 184257.

Results:
| Scenario | Plain average | Target template | Learned interference cancellation | Oracle |
|---|---:|---:|---:|---:|
| Target-only correct locks/960 | 960 | 960 | 960 | 960 |
| Both present correct target locks/960 | 48 | 67 | 960 | 960 |
| Competitor-only false locks/960 | 960 | 960 | 1 | 0 |

The result is conditional on well-separated frequencies, distinct spatial fingerprints, stable known target fingerprint, simulated Gaussian noise, and a spectral peak-based estimator. No online detector field measurements. It does NOT demonstrate radio-frequency reception, a real toroidal antenna, photon-to-capacitance transfer, or cryogenic hardware. The next adversarial test should force signal/interferer spatial overlap and overlapping frequency.
