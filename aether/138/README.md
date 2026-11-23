# AETHER-138 — Instrument identity and protected acquisition receipt contract

**Phase VIII Turn 2 · Local constrained synthetic acceptance PASS · Software readiness 25% · Physical validation 0%.**

## Experiment

40 deterministic seeds × 8 distinct receipt-fault regimes × 24 ticks = **320 episodes / 7,680 decisions per policy**. The local test passed **5,120/5,120** replay, hash-chain, single-action, counter, receipt-gating, safety, clean availability and operational HOLD checks.

| Metric | Signed-only | Mock-receipt-bound |
|---|---:|---:|
| Constructed unsafe ACT | 1,920 | **0** |
| Safe ACT (dry run) | 5,760 | 5,760 |
| Operational ACT | 0 | **0** |

The six fault cases are cloned transport signing key, replayed acquisition counter, stale reference validity, substituted ingress path, forged claim of a hardware flag, and absent hardware receipt. The clean and valid-rotation regimes each preserve **960/960 safe dry-run ACT**.

**A protected acquisition receipt must bind:** device ID, generation, current tick and monotone counter, unpredictable insertion challenge/nonce, actual ingress path, separately established device issuer trust root, reference device and root, reference epoch and calibration validity, conservative uncertainty, and current data. It must not be self-issued by the same software channel being evaluated. The receipt must be independently challenged against actual hardware before becoming operational evidence.

**Critical truth boundary:** All keys and 'protected' roots in this experiment are **HMAC software mocks**. The synthetic reference observation is calculated from ground-truth test state. There is no secure element, real hardware root, trusted physical sensor, calibrated external reference, or measured ingress continuity here. **Every operational action is HOLD** by design; 5,760 safe ACT are hypothetical dry-run authorizations, never real physical permissions.

**Source provenance:** Locally executed Python SHA-256 `ba26f9ab3554bba44d197a9aacbc16e5c329b41c6f41544cd4a3193696c140dd`. The separately authored repository-compatible `experiment.py` is provided as an additional unverified checkout reproducer. Local-run full audit, sample traces, and manifest are in the downloadable ZIP; repo aggregates and manifest explicitly refer to the local run. Live Pages deployment and GitHub checkout replay unverified.

[Python](experiment.py) · [Results](results.csv) · [Manifest](manifest.json) · [Interactive lab](index.html) · [Phase tracker](../PHASE-VIII-STATUS.md).
