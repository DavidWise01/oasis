# AETHER-143 — Adversarial hardware-readiness failure modes

**Phase VIII Turn 7 of 8. Synthetic readiness 87.5%; independently validated physical measurements 0%.**

The locally executed experiment ran 40 seeds × eight scenarios × 24 ticks, **320 cases and 7,680 decisions per policy**. All **5,120/5,120** checks passed: deterministic replay, hash-chain continuity, one action per tick, temporal order, modeled safety, fail-closed evidence, clean and legitimate rotation availability, and operational HOLD.

The signed-only comparator authorized **1,920 unsafe dry-run ACT** against six constructed faults: compromised reference root, replayed attestation, altered uncertainty certificate, falsely claimed same acquisition path, suppressed alarm, and simultaneous compromise of multiple digital signals. The stricter model admitted **zero unsafe dry-run ACT**, preserving **5,760 safe dry-run ACT** (960/960 clean and 960/960 valid rotation).

**The crucial blind spot:** the synthetic protective model uses an external bench which *already knows real risk* via scenario ground truth. The bench key is just another mock HMAC key. Demonstrating that simulated ground truth detects false digital statements **does not validate independent physical measurement**. If the actual bench shares the same compromised ancestor or can itself be forged, software cannot prove the physical truth. The real action gate must continue to HOLD.

**Provenance:** locally executed `experiment.py` SHA-256 `8a629056bcb9fdd67a01939788e62fa42cf90e997dc1b3f3f324608912c3d547`. GitHub's `experiment.py` is a separately authored checkout-oriented reproducer and its numerical replay has not been verified. The repository `results.csv` and `manifest.json` document the local run. Full local audit, 5,120 checks, seed results, source, and traces are available in the attached ZIP.

The next natural bound is **AETHER-144 — Phase VIII readiness integration and evidence freeze**. It must record software completion separately from physical testing and must not invent hardware assurance.

[Experiment](experiment.py) · [Results](results.csv) · [Manifest](manifest.json) · [Interactive Pages lab](index.html) · [Phase tracker](../PHASE-VIII-STATUS.md).
