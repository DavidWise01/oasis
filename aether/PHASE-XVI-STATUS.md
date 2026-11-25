# AETHER Phase XVI — Durable Replay Evidence & Independent Admission

**AETHER-201-RS local durable replay ledger COMMITTED. Phase XVI documentary software progress 1/8 = 12.5%. Authenticated independent external evidence roots: 0. Physical qualification: 0%. Operational ACT: HOLD.**

Phase XV [AETHER-200 documentary freeze](200/decision.json) remains intact: 8/8 software milestones were closed without any independently authenticated original physical evidence or actual alarm observations. Phase XVI shifts from multiplying synthetic gates to on-disk evidence continuity, recovery and independent external custody.

| Turn | Software bound | State | Progress |
|---|---|---|---:|
| 1 | 201 Durable append-only replay ledger and fail-closed recovery | **COMMITTED — local Rust ledger, tests authored** | **12.5%** |
| 2 | 202 OS-process lock ownership and liveness fencing | Planned | 12.5% |
| 3 | 203 Crash recovery with independent signed checkpoint | Planned | 12.5% |
| 4 | 204 Atomic cross-process admission and checkpoint readback | Planned | 12.5% |
| 5 | 205 External custody root and issuer admission | Planned | 12.5% |
| 6 | 206 Independent ancestral cross-check and custody transfer | Planned | 12.5% |
| 7 | 207 Adversarial original evidence admission replay | Planned | 12.5% |
| 8 | 208 Phase XVI software decision and documented freeze | Planned | 12.5% |

## AETHER-201-RS — On-disk replay ledger

- [Rust durable ledger module](rust/src/durable_ledger.rs) stores a JSON Lines SHA-256 hash chain, with exclusive `create_new` lock-file acquisition, original event IDs, capture hashes, challenge nonces, review identifiers and payload digests. A supplied expected head digest and entry count are checked before append.
- The append path writes one ordered record, performs file `sync_all`, requests directory sync, and re-reads the complete hash chain. Recovery rejects incomplete trailing records, altered chain links, unexpected sequence numbers, invalid JSON and duplicate evidence identifiers. An orphaned lock stops new writing rather than guessing stale-lock ownership.
- [18 authored Rust regression tests](rust/tests/durable_ledger.rs) cover disk readback, multi-entry recovery, replay, corruption, stale heads, torn tails, lock contention and fail-closed invariants. **Rust compilation, unit-test execution and Actions status are not independently verified at this point.**
- [4D neon browser laboratory](201/) retains the rotating tesseract and shadow, with synthetic replay, stale-head and torn-tail visualizations. The browser does not use disk fsync or run native Rust. [Protocol](201/protocol.json) records software progress **1/8 = 12.5%**.
- **Limits:** local file fsync does not establish remote durability, physically independent witness custody, cross-machine consensus or authenticated physical acquisition. Lock files are not yet tied to independently checked process liveness. A crash may leave a torn tail that requires supervised recovery. Original independent physical evidence: **0**. Operational ACT remains **HOLD**.
- **Next AETHER-202-RS:** process-authenticated lock holder ownership and OS liveness fencing, without weakening recovery or replay rejection.

`.dlw`
