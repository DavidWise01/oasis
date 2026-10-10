# SHEET 166 — Policy Stability & Recovery Report

## Completed experiments

- Targeted security and correctness: **45/45 PASS**, exit 0.
- Existing predecessor SHEET 165 fault gate, in isolated copy: **15/15 PASS**, exit 0.
- **1,000 synthetic performance windows** with four seeded workload regimes, 3 signed-transition eligibility events. These are synthetic rates, not physical throughput measurements.
- One 128-record authenticated mTLS recovery: **0.542 seconds** end-to-end, **236.2 rows/sec observed**, including a signer-checked downgrade and reconnection. No corresponding S165 A/B trial was executed.

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
| 1 | 2416 | candidate → baseline | 0.745× |
| 2 | 4952 | baseline → candidate | 1.197× |
| 3 | 7216 | candidate → baseline | 0.785× |


## Fault injection

- Restart recovers the decision via Ed25519-signed remote head and separately pinned floor.
- A stale decision or differently signed resource proof is rejected.
- A signer process is SIGKILLed **after external floor fsync but before its local head write**. On restart, the mismatch blocks reads and updates. No automatic pin rollback.
- An unavailable signer at the policy transition causes a failure; the client is **not** silently downgraded.
- The existing protected source/target mTLS protocol validates signed quorum evidence and the final Merkle root after reconnection.

## Interpreting the result

This release measures **stability and recovery correctness**, not improved throughput. The 1,000-window simulation is deterministic and deliberately simplified. The mTLS experiment uses loopback processes on one host, and the inherited 15/15 suite is a targeted subset, not a rerun of the entire historical kernel. Real-world drift thresholds require calibration to each workload and hardware class.