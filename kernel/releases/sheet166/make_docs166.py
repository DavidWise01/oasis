from pathlib import Path
import json, math, statistics
root=Path(__file__).parent
r=json.loads((root/'gate166-results.json').read_text()); n=r['network']; x=r['loadReport']
(root/'README.md').write_text(f'''# SHEET 166 — Hysteresis, Signed Policy Pins & Drift Detection

**Verified:** `0e / PASS`, **{r['checks']}/{r['checks']} new fault/policy checks**, and **15/15** inherited SHEET 165 crash/fallback checks in an independently copied runtime. The complete nested historical test chain was **not** rerun.

## Scope

- `policy166.js` implements bounded-window performance drift classification with asymmetric degradation/re-promotion thresholds, minimum dwell, a signed-recovery cooldown and separate holdout authorization before re-promotion.
- `decision166.js` provides an Ed25519-signed, monotonic policy-decision register and independently retained rollback floor.
- `decision-server166.js` is an independently running mTLS signer. Its client certificate is pinned, and the live signer requires a **signed resource status proof** before accepting a decision.
- `guard166.js` connects the existing SHEET 164/165 authenticated recovery client to the signed decision register, switching clients only after remote decision acknowledgment.
- `gate166.js` verifies policy conditions, 1,000-window synthetic regimes, rollback, interrupted signer persistence, replay, forged proof rejection, outage fail-close, and real mTLS recovery.

## Tests and measurements

| Evidence | Result |
|---|---|
| SHEET 166 targeted checks | {r['checks']}/{r['checks']} PASS |
| Inherited SHEET 165 isolated fault suite | 15/15 PASS (exit 0) |
| Deterministic observation workload | {x['windows']} windows, {x['changes']} authorized transition proposals across {x['regimes']} regimes |
| Real source-to-target recovery | {n['rows']} rows; {n['elapsedSeconds']:.3f} seconds (one-host run) |
| Recovery completion | original Merkle root matched; signed policy generation {n['policyGeneration']} |
| Deliberate forced downgrade | once, after {n['transition']['atRows']} observed committed rows |
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
''')
(root/'BENCHMARK-REPORT.md').write_text(f'''# SHEET 166 — Policy Stability & Recovery Report

## Completed experiments

- Targeted security and correctness: **{r['checks']}/{r['checks']} PASS**, exit 0.
- Existing predecessor SHEET 165 fault gate, in isolated copy: **15/15 PASS**, exit 0.
- **1,000 synthetic performance windows** with four seeded workload regimes, {x['changes']} signed-transition eligibility events. These are synthetic rates, not physical throughput measurements.
- One 128-record authenticated mTLS recovery: **{n['elapsedSeconds']:.3f} seconds** end-to-end, **{n['rows']/n['elapsedSeconds']:.1f} rows/sec observed**, including a signer-checked downgrade and reconnection. No corresponding S165 A/B trial was executed.

## Hysteresis policy

| Parameter | Value |
|---|---:|
| Degradation threshold | ratio below 0.88× baseline |
| Re-promotion threshold | ratio above 1.18× baseline |
| Consecutive weak windows | 3 |
| Consecutive strong windows | 4 |
| Minimum dwell | 48 committed rows |
| After downgrade cooldown | 96 observed rows |
| Drift detection | fast EMA below 0.91× slow EMA for 3 windows |
| Re-promotion permission | explicit verified holdout required |

## Synthetic regime changes

| Transition | At observed rows | Decision | Observed ratio |
|---|---:|---|---:|
'''+''.join(f"| {i} | {e['atRows']} | {e['from']} → {e['to']} | {e['observedRatio']:.3f}× |\n" for i,e in enumerate(x['events'],1))+f'''

## Fault injection

- Restart recovers the decision via Ed25519-signed remote head and separately pinned floor.
- A stale decision or differently signed resource proof is rejected.
- A signer process is SIGKILLed **after external floor fsync but before its local head write**. On restart, the mismatch blocks reads and updates. No automatic pin rollback.
- An unavailable signer at the policy transition causes a failure; the client is **not** silently downgraded.
- The existing protected source/target mTLS protocol validates signed quorum evidence and the final Merkle root after reconnection.

## Interpreting the result

This release measures **stability and recovery correctness**, not improved throughput. The 1,000-window simulation is deterministic and deliberately simplified. The mTLS experiment uses loopback processes on one host, and the inherited 15/15 suite is a targeted subset, not a rerun of the entire historical kernel. Real-world drift thresholds require calibration to each workload and hardware class.
''')
phases=[
 'Pin and verify SHEET 165 ZIP SHA-256','Extract frozen predecessor byte-for-byte','Load current policy checkpoint from separate signer','Obtain challenge-signed Ed25519 head over pinned mTLS','Compare external decision floor and local durable head','Reject stale generation or forked decision hash','Verify resource identity and signed target status','Load trusted baseline and holdout-tested candidate configuration','Initialize observation-local asymmetric hysteresis state','Start source quorum verification','Bind source head to independent Merkle anchor','Open current policy client with approved TLS identity','Fetch signed remote pages with selected prefetch window','Reject out-of-order speculative mutations','Verify resource and source Ed25519 signatures','Check Merkle extension and inclusion proof','Protect target 256-record segment boundary','Commit authorized eight-row (or four-row) batch','Fsync physical segment file','Fsync current Merkle head and cursor','Sample only newly committed row progress','Update fast/slow throughput EMAs','Evaluate three consecutive low-rate windows','Evaluate minimum 48-row dwell','Evaluate three-window workload drift alarm','Classify performance-only degradation','Keep all cryptographic and quorum failures fail-closed','Build signed decision request bound to committed rows','Query authoritative target signed resource status','Verify resource status signature and append position','Bind request to resource journal root','Fetch signer head with fresh nonce','Verify signer Ed25519 signature and old mode','Check expected generation and previous head hash','Check authorized client certificate pin','Check trusted resource status signature at signer','Sign monotonic policy generation and measurement digest','Fsync independently retained external floor first','Fsync signer-local decision head second','Refuse use on a pin/head mismatch after interrupted writes','Return challenge-bound signed acknowledgment','Reverify decision generation and root','Close candidate client and speculative RPCs','Reopen known verified baseline client','Authenticate target durable recovery cursor','Resume remaining rows without duplicate append','Verify final target Merkle root equals source','Persist security audit with no invented performance gains','Start cooldown and suppress immediate re-promotion','Require separate verified holdout for later re-promotion','Reject rapid candidate/baseline oscillation','Reject external signer outage (do not downgrade)','Reject stale signatures, keys, replay and wrong resource root','SIGKILL signer after external fsync for fault test','Verify crash leaves a quarantined unequal head and floor','Restart independent service with same key and pinned state','Verify external rollback floor detects older local restore','Repeat 1,000 deterministic synthetic observation windows','Run actual mTLS source-target fault integration','Rerun isolated SHEET 165 fault suite','Confirm frozen predecessor file SHA-256 matches original','Write reproducible signed-policy and benchmark evidence','Package full predecessor, executable source, ASCII process','Hash sealed release and verify ZIP contents','Commit new source to GitHub without overwriting concurrent work']
assert len(phases)==65,len(phases)
pipe=['OASIS / ROOT0 — SHEET 166 — FULL 65-STAGE EXECUTION PIPE','='*77]
for i,t in enumerate(phases):pipe.append(f'{i:02d}  {t}')
pipe+=['','                    FAULT-CONTAINMENT BRANCH','            ┌────────────────────────────────────┐','  FROZEN    │ AUTHORIZED  │ FAILED SIGNATURE     │','  CHECKPOINT│ TRANSITION  │ STALE FLOOR         │','      │     │      │      │       │             │','      ▼     │      ▼      │       ▼             │','  VERIFY ───┼──> SIGNED ──┼──> FAIL CLOSED       │','            │      │      │                     │','            │      ▼      │                     │','            │ BASELINE    │                     │','            └──────┼───────┴─────────────────────┘','                   ▼','           ORDERED MERKLE APPEND','                   ▼','           SIGNED FINAL ROOT','                   ▼','             NEXT VERIFIED','', 'Critical: the pin is independent of the recovering node, but is a single signer on one physical host.','Cryptographic failures are never treated as performance-only downgrade conditions.']
(root/'KERNEL-ASCII.txt').write_text('\n'.join(pipe)+'\n')
print('wrote docs, phases',len(phases))
