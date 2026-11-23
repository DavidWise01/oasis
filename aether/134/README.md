# AETHER-134 — Bounded reference drift and recalibration economics

**Local synthetic PASS:** 50 seeds × 8 operating regimes × 32 ticks = **400 paired episodes**, **12,800 action decisions per policy**, **5,600/5,600 replay, chain, fail-closed, budget and safety checks**.

The fixed policy recalibrates every eligible tick. The adaptive controller recalibrates every five ticks under a certified low drift envelope, every two ticks under higher certified drift, and immediately when a newly replaced instrument changes generation. In between calibrations, it computes an upper-risk estimate from the last calibration offset plus certified drift-per-tick × age plus certified noise envelope.

| Metric | Fixed | Adaptive |
|---|---:|---:|
| Unsafe ACT | 0 | 0 |
| Safe ACT | 9,000 | 9,000 |
| Safe HOLD | 1,000 | 1,000 |
| Calibrations | 11,900 | 3,650 |

The adaptive policy bought **8,250 fewer calibrations (69.3% reduction)** with no availability regression in these modeled scenarios. This is not measured dollar savings without a validated calibration unit cost.

**Crucial precondition:** The synthetic sensor supplies the true calibration bias at calibration time. It also supplies a certified drift bound and a protected independent abrupt-change flag. Real physical sensing, calibration reference accuracy and independent continuity/alarm mechanisms have **not been verified**. An undetected abrupt jump between periodic checks can still be unsafe. Signed packets alone do not establish a physical drift bound.

**Provenance:** Local executed source SHA-256 `c633be2486fffb814f98e24975b78b40631e108dfc3915a854488b603f739710`. The repository experiment is independently authored from the algorithm and may differ byte-for-byte. Its GitHub-checkout execution and the live Pages site remain unverified.

**Phase VII 6/8 = 75% on constrained synthetic software acceptance**; physical validation is still outstanding.

[Experiment](experiment.py) · [Results](results.csv) · [Manifest](manifest.json) · [Interactive HTML](index.html).
