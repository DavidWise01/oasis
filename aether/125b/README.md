# AETHER-125B — Noninheritable instrument authority

**PASS on bounded synthetic test**: 320 paired episodes (40 seeds × eight replacement scenarios × 32 ticks), **4,480/4,480 deterministic checks**. Guarded controller **0 unsafe actions** versus inherited authority **1,120**. Clean swap recovers after two fresh post-replacement qualified observations.

Eight regimes: clean replacement, stale former calibration, attempted device-ID reuse, counter reset, uncalibrated replacement, bounded-noise replacement, delayed calibration authority, mixed faults.

**Recovery distinction:** a valid new calibration does not authorize ACT. First check certificate device/generation/nonce, protected acquisition epoch and monotonic counter, current packet, truthful noise bounds, and fresh two-read probation. Then independently evaluate the one-sided risk criterion. Recovery is measured at the **first independently risk-admissible fresh packet**. All **320/320** tested episodes matched that oracle; the original AETHER-125 gate failed because 13 noisy episodes required a justified HOLD after calibration readiness.

Safe actions **8,267 inherited vs 7,795 guarded**; extra HOLDs during new-device probation are an availability cost. Synthetic total cost **664,529.6 inherited vs 291,166.4 guarded** under the study's illustrative loss function. The 1,120 inherited unsafe decisions dominate that difference.

**Limitations:** authority signing keys, protected device identity and acquisition counters, truthful sensor noise certificates, challenge secrecy and measurement validity remain assumed. Test is synthetic, not live security assurance. A per-decision 95% risk upper confidence bound does not establish familywise multi-tick safety.

The failed [AETHER-125](../125/) is preserved. Run `python experiment.py` (NumPy, SciPy) to regenerate CSV checks, traces and manifest.
