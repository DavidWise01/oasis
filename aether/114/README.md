# AETHER-114 — Credential Expiry and Key Rotation

**Phase V · Turn 2 of 8 · ACCEPTED on the synthetic gate · 25% completion**

## Invariant

A valid HMAC signature is necessary but **not sufficient** for evidence admission. A key must also be valid at the current observation tick and must match the single authoritative rotation epoch. A previously valid retired key must never regain authorization simply because its signature still verifies.

## Experiment

60 independent synthetic seeds (114001–114060), 7 scenarios, 24 observation ticks per scenario, two paired policies: (a) a keyring-only comparator that verifies the signature but has no expiry gate, and (b) the proposed epoch-bound gate. Data generator makes the true risk 0.3% during safe ticks and 6% during ticks 8–15. A key rotation occurs at tick 12, switching from old key K0 to K1. Packet fields include stream, sequence, tick, error count, certified status, epoch, key identifier, arrival time and HMAC signature. True risk is hidden from both controllers.

**Test keys are deliberately disclosed fixtures; never deploy them.** In the expired/revoked/rollback scenarios, old-key packets have valid signatures but falsely declare zero errors during the hazard interval. This is a concrete test of the expiry rule, not a claim that the controller identifies forged origins.

## Results

| Scenario | Keyring-only unsafe | Epoch-bound unsafe | Clean safe actions retained |
|---|---:|---:|---:|
| Clean rotation | 0 | 0 | 960 / 960 |
| Expired old key | 240 | 0 | — |
| Epoch rollback | 240 | 0 | — |
| Revoked old key | 240 | 0 | — |
| Unknown key | 0 | 0 | — |
| Tampered epoch | 0 | 0 | — |
| Delayed packet | 0 | 0 | — |
| **All** | **720** | **0** | **100% in clean rotation** |

The verifier passed **3,360 of 3,360** deterministic replay, hash chain, fail-closed, and action admissibility checks across 840 policy-scenario-seed cases. On the synthetic cost formula, keyring-only totaled 375,192.9 and epoch-bound totaled 138,672.9 (difference 236,520); this large difference is driven by three deliberately constructed attack scenarios and should not be projected to operating environments.

## Acceptance

1. All deterministic and chain checks pass — **PASS**.
2. At least 95% of clean safe actions survive the rotation — **PASS (100%)**.
3. No unsafe authorization across attack scenarios under epoch validation — **PASS (0)**.
4. Never exceed keyring-only unsafe authorizations — **PASS**.

## Scope limits

The controller assumes an authoritative, truthful, available rotation schedule. A compromised active key, stolen key schedule, delayed revocation notification, signed but dishonest sensor report, and fabricated independent roots are outside the demonstrated coverage. HMAC authentication proves possession of a secret but does not establish the truth or independence of observations. These are not production safety guarantees.

**Reproduce:** `python aether/114/experiment.py` (NumPy and SciPy). Outputs `results.csv`, `checks.csv`, `seed_results.csv`, `trace_samples.csv`, and `manifest.json`. Identical seed and source reproduce the test.

[GitHub Pages lab](https://davidwise01.github.io/oasis/aether/114/) · [Phase V progress](../PHASE-V-STATUS.md) · [AETHER-113](../113/).

**Next: AETHER-115 — Rotation-Schedule Freshness and Revocation-Notice Delays.** A signed packet should not authorize an action merely because the controller hasn't yet learned of a key retirement.

`{24/[2]/[4]/(3)/(3)/(1)/(1)} · {{i}} · .dlw`
