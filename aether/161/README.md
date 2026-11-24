# AETHER-161 — Phase XI Physical Evidence Acquisition Boundary

**Phase XI, Turn 1/8 · 12.5% synthetic software acquisition-protocol readiness · 0% empirical physical qualification.**

Locally executed: 25 seeds × eight scenario types × 20 ticks × two admission policies = 200 episodes and 4,000 decisions per policy, with **3,200/3,200 deterministic tests passed**. Signed-only policy authorized **1,200 unsafe synthetic dry-run ACT**. The acquisition-intake policy authorized **zero unsafe synthetic ACT**, preserving **2,800 safe synthetic dry-run ACT**, including 500/500 clean and 500/500 mock device rotation.

Six faults: blank instrument serial, self-issued certificate, changed original raw capture, missing clock provenance, shared calibration ancestry and fabricated physical-qualification flag. Raw bytes are canonicalized and SHA-256 tested; issuer, generation, challenge nonce, instrument/reference binding and conservative uncertainty upper bound must agree. The controller is not passed truth labels. Its physical qualification flag is always **false** because mock reference data never becomes real laboratory evidence.

The authoritative [physical acquisition register](physical_acquisition_register.json) holds *null* instrument serials, reference certificates, traceability, physical challenge records and genuine sample hashes. No real instrument measurement was supplied, no accrediting body was checked and no actual acquisition path was verified. Operational ACT remains HOLD.

**Reproducibility:** Exact locally executed script `local_audit.py` SHA-256 `39a08d9bd277b5a96a10efc92ec58c4634aa74725c45d4519221b33c78e81e2d` is in the companion evidence ZIP with 3,200 check rows, all seed results, sample SHA-256-chained traces and manifest. The GitHub `experiment.py` is a different, more complete standalone source and has **not yet been independently executed from checkout**. Live Pages deployment also remains unverified.

[Python source](experiment.py) · [Results](results.csv) · [Manifest](manifest.json) · [Evidence register](physical_acquisition_register.json) · [Interactive lab](index.html) · [Phase XI tracker](../PHASE-XI-STATUS.md).

**Next AETHER-162:** source-of-truth physical instrument identity and independent calibration evidence intake. Software readiness target 25%, physical qualification 0% without authenticated hardware records.
