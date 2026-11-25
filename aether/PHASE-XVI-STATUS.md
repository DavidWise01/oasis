# AETHER Phase XVI — Durable Replay Evidence & Independent Admission

**AETHER-208-RS PHASE XVI FINAL DOCUMENTARY QUALIFICATION FREEZE COMMITTED. Phase XVI software protocol CLOSED: 8/8 = 100%. Authenticated independent external evidence roots: 0. Authenticated original physical captures: 0. Independent remote checkpoints: 0. Physical qualification: 0%. Operational ACT: HOLD.**

Phase XV [AETHER-200 documentary freeze](200/decision.json) remains intact: 8/8 software milestones were closed without any independently authenticated original physical evidence or actual alarm observations. Phase XVI shifts from multiplying synthetic gates to on-disk evidence continuity, recovery and independent external custody.

| Turn | Software bound | State | Progress |
|---|---|---|---:|
| 1 | 201 Durable append-only replay ledger and fail-closed recovery | **COMMITTED — local Rust ledger, tests authored** | **12.5%** |
| 2 | 202 OS-process lock ownership and liveness fencing | **COMMITTED — local Linux PID/starttime/boot ID verification; never automatic reclaim** | **25%** |
| 3 | 203 Crash recovery with independent signed checkpoint | **COMMITTED — Rust externally pinned documentary checkpoint gate** | **37.5%** |
| 4 | 204 Atomic cross-process admission and checkpoint readback | **COMMITTED — one local OS lock across checkpoint validation, append and readback** | **50%** |
| 5 | 205 External custody root and issuer admission | **COMMITTED — synthetic pinned issuer, holder and rotation gate only** | **62.5%** |
| 6 | 206 Independent ancestral cross-check and custody transfer | **COMMITTED — signed exact-transition admission under one local process lock** | **75%** |
| 7 | 207 Adversarial original evidence admission replay | **COMMITTED — persisted replay registry and signed revocation amendment** | **87.5%** |
| 8 | 208 Phase XVI software decision and documented freeze | **CLOSED — machine-readable Rust documentary freeze; physical ACT HOLD** | **100%** |

## AETHER-208-RS — Phase XVI documentary qualification decision and historical freeze

- **Phase XVI software contract CLOSED: 8/8 = 100%.** This is completion of authored documentary software milestones, not independently executed Rust qualification or real-world physical authorization. Independently authenticated external evidence roots: **0**; authenticated original physical captures: **0**; independently retained remote checkpoints: **0**; physical qualification **0%**; ACT **HOLD**.
- [Native Rust freeze evaluator](rust/src/phase_xvi_freeze.rs) checks AETHER-201–208 sequence and coverage, software closure state, unresolved evidence categories, prior Phase XV freeze, historical append-only intent, absence of physical ACT and accurate disclosures of unverified compilation/CI/browser deployment.
- [39 authored Rust regression tests](rust/tests/phase_xvi_freeze.rs) cover the documentary readback, missing/reordered bounds, fabricated external custody, physical hardware or remote checkpoints, forged test/CI/Pages success, omission of crash-recovery gaps, claimed Git branch immutability and ACT promotion. **Actual Rust compilation and test execution remain unverified.**
- [Machine-readable final decision](208/decision.json) and [protocol](208/protocol.json) distinguish **100% software phase progress** from **0% physical qualification**. A recorded documentary freeze is not technical immutability of a mutable Git branch.
- [Full neon 4D HTML laboratory](208/) preserves the animated 16-vertex / 32-edge shadow tesseract and reads final decision JSON in an interactive inspection panel. It does not run Rust, verify independent physical evidence or imply the live Pages deployment was observed.
- **Unresolved HOLD boundaries:** two-file ledger/registry update is not crash-atomic; externally held rollback anchors are absent; independent issuer/custodian origin remains unverified; revocation authority and physical alarm evidence have not been externally authenticated; the Linux lock is local, not distributed fencing. Fail-closed incident review, not automatic repair or physical ACT, remains the allowed response.
- No AETHER-201–207 historical source is overwritten to claim new physical evidence. A new phase must begin only with explicitly declared trust and recovery requirements. `.dlw`

## AETHER-207-RS — Persistent authorization replay and signed revocation epoch

- [Native Rust authorization registry](rust/src/authorization_registry.rs) stores the exact ledger head and entry count, consumed admission and transition identifiers/nonces/intent hashes, separately pinned issuer/holder fingerprints, a monotonically increasing revocation epoch and signed revocation amendment IDs.
- Under a **single verified Linux process lock**, it rechecks the registry against the full hash-chained ledger, adjudicates AETHER-206 signed checkpoint/custody/transition, fsyncs the journal, then publishes the updated registry via a fsynced pending file and rename with directory sync.
- A journal/registry mismatch, corrupt registry, unauthorized revocation, stale epoch, reused authorization, or abandoned pending transaction **fails closed**. Two-file persistence is **not a single crash-atomic transaction**; after an interrupted append, the next admission is withheld pending independent adjudication.
- A separate P-256 signed revocation amendment binds the old/new epoch, journal head, amended revoked fingerprints, and distinct revocation-authority root/operator/administrator. Revoked keys cannot be unrevoked via this interface. A caller-provided external-authentication boolean does not establish independent custody.
- [41 authored Rust adversarial tests](rust/tests/authorization_registry.rs) cover integrated admission, persisted restart readback, replay, rollback, corrupt/missing registry, pending write, changed pins/epochs, forged and replayed revocation, separate authority and fail-closed ACT. **Compilation, tests and CI runtime are not yet independently verified.**
- [Animated 4D neon lab](207/) preserves the rotating tesseract and shows registry failure scenarios. The browser does not run Rust or persist disk state. [Protocol](207/protocol.json) records **Phase XVI 7/8 = 87.5%**, physical qualification **0%**, operational ACT **HOLD**.
- **Remaining limitation:** a privileged adversary can roll back the ledger and registry together absent an independently retained checkpoint; no physical acquisition or external custody root has been authenticated. Trust pin initial enrollment remains a documentary input. No distributed fencing, cross-host consensus or automatic recovery is claimed.
- **Next AETHER-208-RS:** close Phase XVI with a machine-readable documentary freeze and explicitly record unresolved external-custody, crash-recovery and physical-evidence requirements. `.dlw`

## AETHER-206-RS — One custody admission, one exact signed journal transition

- [Native Rust custody-commit verifier](rust/src/custody_commit.rs) binds **both issuer and holder P-256 signatures** to the same canonical transition intent: original event digest and individual fields, checkpoint SHA-256, custody admission SHA-256, expected journal head, sequence, ledger identity and unique authorization nonce.
- Under **one Linux OS-owned lock**, the gate checks the AETHER-203 signed checkpoint against the full journal, re-adjudicates the AETHER-205 issuer/holder admission, verifies pinned holder and issuer keys and exact transition signatures, compares expected head and count, then calls AETHER-204's [guarded durable append](rust/src/durable_ledger.rs). The write is fsynced and journal read back before the lock is released.
- [24 authored Rust regression tests](rust/tests/custody_commit.rs) cover the intended synthetic path plus competing writers, stale head/sequence and intervening prior writer, changed original event and checksum, mismatched checkpoint or admission, forged holder/issuer signatures, revoked credentials, replayed authorization IDs/nonces, unauthorized origins, torn journal tail and orphaned locks. **Compilation, tests and Actions results remain unverified.**
- [Animated neon 4D GitHub Pages-ready lab](206/) retains the 16-vertex/32-edge tesseract and illustrates six documentary scenarios. The browser does not execute native Rust. [Protocol](206/protocol.json) records **Phase XVI 6/8 = 75%**, authenticated independent external custody **0**, physical qualification **0%**, ACT **HOLD**.
- **Limits:** custody-policy trust flags and independently provisioned pins remain supplied evidence, not out-of-band authenticity proof; the authorization replay set and revocation epoch have not been bound to an independent durable registry. The Linux lock does not establish distributed atomic external custody, and the mutable local directory is not a hardened hostile-filesystem boundary. No real original physical measurements or independently held checkpoint have been authenticated.
- **Next AETHER-207-RS:** adversarial original-evidence admission replay with custody revocation and independent ancestry under realistic persisted registry state. `.dlw`

## AETHER-205-RS — Pinned custody issuer, holder and independent rotation admission

- [Rust external custody admission verifier](rust/src/external_custody.rs) checks real P-256 signatures from the issuer and holder over the same custody record; exact SHA-256 pins for issuer and holder public keys; original checkpoint digest; ledger ID; declared source, holder and issuer root/operator/administrator ancestry; policy epoch, replayed nonces, and revocation lists.
- A holder-key change must carry a separately signed [rotation approval](rust/src/external_custody.rs), with old and new holder fingerprints, independent approver root/operator/administrator, a pinned rotation authority key, policy epoch, unique approval nonce and revocation checks. Otherwise rotation fails closed.
- [33 authored Rust integration tests](rust/tests/external_custody.rs) cover two-signature consistency, shared/self-issued roots, revocation, replay, key substitution, missing external origin, forged signatures and unauthorized or recycled rotation authority. **Cargo/Actions execution remains unverified.**
- [4D neon HTML lab](205/) retains the rotating 16-vertex/32-edge tesseract and six illustrative custody scenarios. The browser does not perform native Rust checks or external identity authentication. [Protocol](205/protocol.json) records **Phase XVI 5/8 = 62.5%**.
- **Trust boundary:** actual issuer and holder independence is *not* authenticated by root labels or caller-set booleans. No externally authenticated custody holders or real original physical evidence have been provided. This gate is documentary only and is not yet bound atomically to the AETHER-204 append critical section. Physical qualification remains **0%**, operational ACT **HOLD**.
- **Next AETHER-206-RS:** independent custody admission integrated with the same locked ledger write, including revocation and ancestry readback. `.dlw`

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
