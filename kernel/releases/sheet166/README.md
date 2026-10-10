# SHEET 166 — Hysteresis, Signed Policy Pins & Drift Detection

**Verified:** `0e / PASS`, **45/45 new fault/policy checks**, and **15/15** inherited SHEET 165 crash/fallback checks in an independently copied runtime. The complete nested historical test chain was **not** rerun.

## Scope

- `policy166.js` implements bounded-window performance drift classification with asymmetric degradation/re-promotion thresholds, minimum dwell, a signed-recovery cooldown and separate holdout authorization before re-promotion.
- `decision166.js` provides an Ed25519-signed, monotonic policy-decision register and independently retained rollback floor.
- `decision-server166.js` is an independently running mTLS signer. Its client certificate is pinned, and the live signer requires a **signed resource status proof** before accepting a decision.
- `guard166.js` connects the existing SHEET 164/165 authenticated recovery client to the signed decision register, switching clients only after remote decision acknowledgment.
- `gate166.js` verifies policy conditions, 1,000-window synthetic regimes, rollback, interrupted signer persistence, replay, forged proof rejection, outage fail-close, and real mTLS recovery.

## Tests and measurements

| Evidence | Result |
|---|---|
| SHEET 166 targeted checks | 45/45 PASS |
| Inherited SHEET 165 isolated fault suite | 15/15 PASS (exit 0) |
| Deterministic observation workload | 1000 windows, 3 authorized transition proposals across 4 regimes |
| Real source-to-target recovery | 128 rows; 0.542 seconds (one-host run) |
| Recovery completion | original Merkle root matched; signed policy generation 1 |
| Deliberate forced downgrade | once, after 48 observed committed rows |
| Invalid Ed25519 / rollback / incorrect floor | fail closed |
| Signer killed after pin fsync | fail closed pending manual reconciliation |
| Signer unavailable during downgrade | **no baseline client reopened** |

The reported network duration is **not a head-to-head performance comparison** because the test deliberately injects a slow observation clock and switches policies mid-run. No claim of a speedup is made.

## Running

```bash
cd sheet166
node gate166.js
```

The signed floor and signer key are separate from the recovering resource process, but **all services are running on the same physical host** in this release.

## Security / engineering limitations

The signer authenticates an authorized client and checks resource status cryptographically, but it **cannot independently attest actual wall-clock throughput**; the client supplies measurement evidence. This is a single signer, **not a 2/3 distributed consensus authority**. `pin -> local` torn persistence intentionally quarantines state until a reviewed reconciliation; no automatic repair or production UI is included. Hysteresis state is observation-local and recalculated after restart from the signed active mode; only signed policy transitions are durable. The complete historical regression chain and cross-host partition safety are not established.