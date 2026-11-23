# AETHER-127C — Guaranteed microprobe coverage, accepted synthetic test

The preceding [AETHER-127](../127/) failed because nonlinear response faults passed four fixed calibration points. [AETHER-127B](../127b/) added 88 randomly placed microprobes but **failed clean availability** (1,918 → 1,588), because sampling did not guarantee a radius-1 input net.

**AETHER-127C** keeps the same 88 microprobes but guarantees a radius-1 cover of integer risk counts 0–100 using a random parity grid with concealed extra interior points. This is a *constrained calibration-domain result*, not a general nonlinear sensor guarantee.

New holdout: 60 seeds × 8 unseen scenarios × 32 ticks = **480 paired episodes**, **15,360 decisions per policy**, **6,720/6,720** deterministic/replay/coverage checks. Frozen adaptive controller **665 unsafe ACT**; radius-1 coverage controller **0 unsafe ACT** under modeled nonlinear conditions. Clean safe actions remained **1,918/1,918**. Total safe actions **8,066 → 6,867**. Probe purchases **47,640 → 1,399,320**; illustrative synthetic cost **729,216.8 → 3,151,809.6**.

**Strict limitations:** Current code tests a simulated physical response using known synthetic fault physics; a real verifier would need trusted opaque same-path test injection and sensor response retrieval. A trusted local regularity bound over the full operational count domain is also required; discrete point probes alone cannot certify arbitrary changes between samples, outside 0–100, or selectively adversarial behavior. This test does not establish a complete physical device trust root. An untrusted response-domain bound must yield HOLD, not broader permission.

Run `python experiment.py` in repository layout with NumPy and SciPy. The local source hashes need checkout confirmation before claiming identical replay of all rows.
