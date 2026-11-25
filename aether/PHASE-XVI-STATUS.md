# AETHER Phase XVI — Durable Replay Evidence & Independent Admission

**AETHER-204-RS ATOMIC CHECKPOINT ADMISSION & DURABLE READBACK GATE COMMITTED. Phase XVI documentary software progress 4/8 = 50%. Authenticated independent external evidence roots: 0. Physical qualification: 0%. Operational ACT: HOLD.**

Phase XV [AETHER-200 documentary freeze](200/decision.json) remains intact: 8/8 software milestones were closed without any independently authenticated original physical evidence or actual alarm observations. Phase XVI shifts from multiplying synthetic gates to on-disk evidence continuity, recovery and independent external custody.

| Turn | Software bound | State | Progress |
|---|---|---|---:|
| 1 | 201 Durable append-only replay ledger and fail-closed recovery | **COMMITTED — local Rust ledger, tests authored** | **12.5%** |
| 2 | 202 OS-process lock ownership and liveness fencing | **COMMITTED — local Linux PID/starttime/boot ID verification; never automatic reclaim** | **25%** |
| 3 | 203 Crash recovery with independent signed checkpoint | **COMMITTED — Rust externally pinned documentary checkpoint gate** | **37.5%** |
| 4 | 204 Atomic cross-process admission and checkpoint readback | **COMMITTED — one local OS lock across checkpoint validation, append and readback** | **50%** |
| 5 | 205 External custody root and issuer admission | Planned | 50% |
| 6 | 206 Independent ancestral cross-check and custody transfer | Planned | 50% |
| 7 | 207 Adversarial original evidence admission replay | Planned | 50% |
| 8 | 208 Phase XVI software decision and documented freeze | Planned | 50% |

## AETHER-204-RS — One-lock checkpoint admission and fsynced readback

- [Rust recovery checkpoint](rust/src/recovery_checkpoint.rs) now acquires the verified Linux process-owner lock **before** reading ledger history, evaluating the pinned holder-signed checkpoint or comparing the expected head and sequence.
- [Durable ledger](rust/src/durable_ledger.rs) exposes a guarded append internal API. The **same guard** is retained through replay screening, byte append, file `sync_all`, parent directory sync, complete journal readback and record identity verification. Ordinary durable appends retain their own exclusive lock acquisition.
- [Process identity verifier](rust/src/process_liveness.rs) now offers `verify_for` for a specific lock path. It checks recorded owner metadata and inode identity and rechecks Linux OS liveness before and after the protected operation. An invalidated guard never authorizes lock seizure.
- [20 authored Rust regression tests](rust/tests/atomic_checkpoint.rs) cover the intended successful documentary append and readback, competing writers, stale counts and heads, an intervening writer, truncated/corrupt/torn history, replay, forged checkpoint, missing custody, malformed lock and owner/inode mutation. **Cargo compilation, all regression execution and GitHub Actions status are not independently verified.**
- [Animated 4D neon lab](204/) preserves the 16-vertex, 32-edge shadow tesseract and illustrates six admission outcomes; it cannot execute Rust or validate external custody. [Protocol](204/protocol.json) records **Phase XVI 4/8 = 50%**, physical qualification **0%**, operational ACT **HOLD**.
- **Remaining limitations:** externally authenticated checkpoint custody and remote readback have not been supplied; caller policy booleans are not independent proof. A mutable hostile directory or remote filesystem is beyond this local guard. Torn journal tails remain fail-closed and require controlled recovery. No physical ACT, lock reclamation, or operational promotion is allowed.
- **Next AETHER-205-RS:** external holder identity/root admission and independent custody-proof verification, rather than additional synthetic self-issued certificates. `.dlw`

## AETHER-203-RS — Signed independent recovery checkpoint and rollback detection

- [Native Rust checkpoint gate](rust/src/recovery_checkpoint.rs) verifies ECDSA P-256 signatures over ordered checkpoint metadata, an independently provisioned holder-key fingerprint and exact checkpoint digest, chain predecessor, source-holder ancestry separation, replayed checkpoint identifiers and nonces, and ledger ID.
- The verifier reads the [durable ledger](rust/src/durable_ledger.rs) through its already implemented JSONL hash-chain verifier. It rejects a **locally valid but truncated prefix**, deleted history, substituted checkpoint signatures or full-history divergence from the independently pinned checkpoint. Missing independent holder custody causes HOLD.
- [25 authored Rust regression tests](rust/tests/recovery_checkpoint.rs) include valid synthetic signatures, complete rollback, valid-prefix truncation, independent digest substitutions, forged signatures, shared ancestry, replay, corrupt trailing bytes and documentary-gated append.
- The [neon 4D laboratory](203/) preserves the animated 16-vertex/32-edge hypercube and displays six synthetic checkpoint failure paths. It does not run Rust or authenticate any physical or externally held records. [Protocol](203/protocol.json) records **Phase XVI 3/8 = 37.5%**, physical 0%, ACT HOLD.
- **Limits:** no real externally authenticated custodian or independently held checkpoint was supplied; holder-authentication flags in the Rust policy are not proof of origin. Ledger append checks its expected head under the process lock, but the external checkpoint proof is currently evaluated before that lock, leaving stronger atomic admission for AETHER-204. No lock takeover or history repair is enabled.
- **Next AETHER-204-RS:** inspect checkpoint under the exact acquired OS process lock and seal a locally durable checkpoint commitment only after full readback. `.dlw`

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
