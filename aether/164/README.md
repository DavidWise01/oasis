# AETHER-164 — Calibration Traceability and Physical Uncertainty Evidence

**Phase XI Turn 4/8: 50% synthetic software readiness; 0% empirical physical qualification.**

The exact locally executed experiment passed **3,200/3,200** checks over **25 seeds × eight cases × 20 ticks × two policies**, with **200 episodes / 4,000 decisions per policy**. A signed-only comparator permitted **1,200 unsafe synthetic dry-run ACT**, while the guarded controller permitted **0 unsafe** and retained **2,800 safe dry-run ACT**. Clean and legitimate reference rotation retained **500/500** safe actions each. Operational ACT remained HOLD.

The six synthetic faults were missing uncertainty contributor, shared calibration ancestry, expired calibration, understated resolution, unsupported coverage and contradictory reference/bench reading. Model standard uncertainty components: calibration `.0010`, repeatability `.0005`, resolution `.0004`, drift `.0006`; RSS combination with `k=2` expanded uncertainty. Coverage rule: one-sided 90% Wilson lower bound supports a claimed 95% over 120 **simulated** held-out observations. These figures are policy fixtures, **not physical calibration measurements**.

Actual instrument, laboratory issuer, accreditation, original capture, physical uncertainty and independent source ancestry are not verified. See the [null-filled physical register](physical_calibration_register.json). Real physical qualification stays **0%** and operational permission stays **HOLD**.

Full locally executed source SHA-256: `93f5d7d536209ff7b1ac079b2e27c4b4417f6519e9828390e665b4181602f798`. Complete evidence ZIP SHA-256: `9bce6347fdd891c65036e3ba9d6a4c24267b7beed58042ac7dc9cea3ea3117fb`, containing source, all checks, seed results, sample SHA-256 traces and manifest.

**Reproduction boundary:** GitHub `experiment.py` is a shorter independently authored reproducer, not the exact local source and not yet independently checkout-tested. HTML is committed for Pages; live deployment not verified.

[GitHub Python companion](experiment.py) · [Results](results.csv) · [Manifest](manifest.json) · [Physical register](physical_calibration_register.json) · [Interactive laboratory](index.html) · [Phase XI tracker](../PHASE-XI-STATUS.md).

**Next bound AETHER-165:** a real same-path challenge evidence contract, preserving physical evidence as OPEN/0% absent original instrument recordings.
