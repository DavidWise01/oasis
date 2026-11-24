# AETHER-162 — Genuine instrument and reference identity intake

**Phase XI Turn 2/8 · 25% synthetic protocol readiness · 0% empirical physical qualification.**

The locally executed `aether162/experiment.py` (SHA-256 `f296840cb73970d98787e81e706d96e15e72170cfa1db16d8ea6fd9e06543a01`) ran 25 seeds × eight cases × 20 ticks × two policies. It passed **3,200/3,200 deterministic checks**, with **200 episodes and 4,000 decisions per policy**.

Signed-only comparator: **1,200 unsafe synthetic dry-run ACT**. Identity gate: **0 unsafe**, retaining **2,800 safe synthetic dry-run ACT** (500 clean, 500 legitimate mock rotation). Operational ACT = 0.

Six faults: missing DUT serial; cloned DUT identity with challenge-response mismatch; unknown calibration certificate issuer; false accreditation claim; self-rooted calibration ancestry; and absent DUT attestation. The gate checks simulated manufacturer/model, serial, issuer certificate, signed reference register, separate proof response, challenge nonce, original raw sample hash and uncertainty upper bound.

**Provenance limitation:** DUT key, laboratory issuer, reference registry, and all readings are generated in the same test fixture. A matching mock registry cannot prove real independent authority, device possession, certificate issuance or metrological traceability. [Physical identity register](physical_identity_register.json) leaves all real hardware and lab fields null. **Physical qualification: 0%. Every real operational action stays HOLD.**

Exact locally executed code, 3,200 checks, seed results, SHA-256 chained traces, physical register, README and manifest are in the verified ZIP (SHA-256 `fb1bd1b73f49a3e0ec17561c8e077fb92db28c951d803b5c181222d709ebb55f`). GitHub's `experiment.py` is a separately authored condensed reproduction; independent checkout replay and live GitHub Pages deployment remain unverified.

[Python demo](experiment.py) · [Results](results.csv) · [Manifest](manifest.json) · [Physical register](physical_identity_register.json) · [Interactive laboratory](index.html) · [Phase XI tracker](../PHASE-XI-STATUS.md).

**Next AETHER-163:** original physical capture intake and a traceable physical clock, with no physical qualification claims absent actual evidence.
