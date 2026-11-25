# AETHER Phase XVI — Durable Replay Evidence & Independent Admission

**AETHER-202-RS Linux process identity and liveness-fenced local lock COMMITTED. Phase XVI documentary software progress 2/8 = 25%. Authenticated independent external evidence roots: 0. Physical qualification: 0%. Operational ACT: HOLD.**

Phase XV [AETHER-200 documentary freeze](200/decision.json) remains intact: 8/8 software milestones were closed without any independently authenticated original physical evidence or actual alarm observations. Phase XVI shifts from multiplying synthetic gates to on-disk evidence continuity, recovery and independent external custody.

| Turn | Software bound | State | Progress |
|---|---|---|---:|
| 1 | 201 Durable append-only replay ledger and fail-closed recovery | **COMMITTED — local Rust ledger, tests authored** | **12.5%** |
| 2 | 202 OS-process lock ownership and liveness fencing | **COMMITTED — local Linux PID/starttime/boot ID verification; never automatic reclaim** | **25%** |
| 3 | 203 Crash recovery with independent signed checkpoint | Planned | 25% |
| 4 | 204 Atomic cross-process admission and checkpoint readback | Planned | 25% |
| 5 | 205 External custody root and issuer admission | Planned | 25% |
| 6 | 206 Independent ancestral cross-check and custody transfer | Planned | 25% |
| 7 | 207 Adversarial original evidence admission replay | Planned | 25% |
| 8 | 208 Phase XVI software decision and documented freeze | Planned | 25% |

## AETHER-202-RS — OS-observed process-owner identity and liveness

- [Native Linux lock guard](rust/src/process_liveness.rs) records the actual process PID, Linux `/proc/<pid>/stat` field 22 process-start ticks and kernel boot UUID in mode-0600 lock metadata created exclusively via `create_new`. The lock content and directory are synchronized before the lock is admitted.
- The owner monitor differentiates **ALIVE**, **EXITED** (including PID reuse or zombie), **UNKNOWN** and **ABSENT**, explicitly setting `may_reclaim = false` for every state. Malformed or unreadable metadata and unsupported operating systems fail closed.
- Release verifies the original owner record and file identity (device/inode on Unix) before removing its own lock; external mutation causes refusal. **This local mechanism is not an OS pidfd, distributed lease, or defense against all adversarial directory races.**
- [AETHER-201 durable append module](rust/src/durable_ledger.rs) now uses the new process-aware lock guard, preserving hash-chained JSONL append, file/directory fsync, replay protection and torn-tail rejection.
- [20 authored Linux integration tests](rust/tests/process_liveness.rs) cover kernel self-identity, nested process-name parsing, private permissions, PID reuse, zombie states, boot-ID mismatch, lock contention, tampering, inode replacement, orphaned locks and guarded release. **Rust compilation and GitHub Actions run results remain unverified.**
- [4D neon browser laboratory](202/) preserves the rotating 16-vertex/32-edge tesseract with simulated liveness states and NO-RECLAIM behavior. The browser does not access `/proc` or run Rust. [Protocol](202/protocol.json) records **2/8 = 25%**, physical qualification **0%**, and operational ACT **HOLD**.
- **Next AETHER-203-RS:** an independently signed remote checkpoint and fail-closed rollback/torn-tail adjudication. A process-exit observation alone never authorizes custody takeover. `.dlw`

## AETHER-201-RS — On-disk replay ledger

- [Rust durable ledger module](rust/src/durable_ledger.rs) stores a JSON Lines SHA-256 hash chain, with exclusive `create_new` lock-file acquisition, original event IDs, capture hashes, challenge nonces, review identifiers and payload digests. A supplied expected head digest and entry count are checked before append.
- The append path writes one ordered record, performs file `sync_all`, requests directory sync, and re-reads the complete hash chain. Recovery rejects incomplete trailing records, altered chain links, unexpected sequence numbers, invalid JSON and duplicate evidence identifiers. An orphaned lock stops new writing rather than guessing stale-lock ownership.
- [18 authored Rust regression tests](rust/tests/durable_ledger.rs) cover disk readback, multi-entry recovery, replay, corruption, stale heads, torn tails, lock contention and fail-closed invariants. **Rust compilation, unit-test execution and Actions status are not independently verified at this point.**
- [4D neon browser laboratory](201/) retains the rotating tesseract and shadow, with synthetic replay, stale-head and torn-tail visualizations. The browser does not use disk fsync or run native Rust. [Protocol](201/protocol.json) records software progress **1/8 = 12.5%**.
- **Limits:** local file fsync does not establish remote durability, physically independent witness custody, cross-machine consensus or authenticated physical acquisition. Lock files are not yet tied to independently checked process liveness. A crash may leave a torn tail that requires supervised recovery. Original independent physical evidence: **0**. Operational ACT remains **HOLD**.
- **Next AETHER-202-RS:** process-authenticated lock holder ownership and OS liveness fencing, without weakening recovery or replay rejection.

`.dlw`
