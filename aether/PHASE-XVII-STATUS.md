# AETHER Phase XVII — External Recovery Anchors and Independently Held Evidence

**AETHER-211-RS MONOTONIC RECEIPT EXTENSION & SIGNED HOLDER ROTATION GATE COMMITTED. Phase XVII documentary software progress 3/8 = 37.5%. Independently authenticated remote receipts: 0. Authenticated original physical captures: 0. Physical qualification: 0%. Operational ACT: HOLD.**

Phase XVI's [AETHER-208 freeze](208/decision.json) remains unchanged, with 8/8 software milestones closed but original physical evidence, independent remote custody, and runtime certification unresolved. A locally valid journal and registry can be rolled back together; Phase XVII examines the need for externally anchored history and independently adjudicated recovery.

| Turn | Milestone | State | Progress |
|---|---|---|---:|
| 1 | 209 Remote-anchor verifier and joint-rollback screening | **COMMITTED — synthetic signed anchor and ledger/registry comparison** | **12.5%** |
| 2 | 210 Independent anchor-receipt custody envelope and durable replay | **COMMITTED — local receipt journal, not independent external custody** | **25%** |
| 3 | 211 Signed external-receipt refresh and nonrollback chain | **COMMITTED — monotonic predecessor and forward history; rotation checks** | **37.5%** |
| 4 | 212 Crash recovery incident proof without automatic repair | Planned | 37.5% |
| 5 | 213 Independently retained control-ancestry evidence | Planned | 37.5% |
| 6 | 214 Cross-host receipt-consistency and equivocation screening | Planned | 37.5% |
| 7 | 215 Adversarial remote custody and recovery qualification | Planned | 37.5% |
| 8 | 216 Phase XVII documentary software freeze | Planned | 37.5% |

## AETHER-211-RS — Monotonic receipt history and independent holder-rotation screening

- [Rust forward-extension module](rust/src/monotonic_receipt.rs) requires every subsequent receipt to bind the **exact SHA-256 digest of the previous anchor**, increase the ledger entry count, change the ledger head digest, and retain a nondecreasing registry revocation epoch. Source and issuer root/operator/administrator ancestry may not silently change. A later timestamp alone never proves forward progression.
- Changes to holder identity, ancestry or pinned key require a separately signed P-256 [rotation record](rust/src/monotonic_receipt.rs) bound to old/new anchor digests, old/new holder identity and fingerprints, independent rotation authority ancestry and a unique authorization nonce. Independent authority key pin and external-origin qualification are required as documentary inputs; no self-declared real-world independence is accepted as proof.
- The [receipt custody module](rust/src/receipt_custody.rs) now offers `ingest_monotonic`, invoking extension checks **inside its existing exclusive Linux process-owned lock**, before existing signed-anchor screening, append, fsync and full journal readback. Earlier `ingest` remains available for historical compatibility; use the new function for forward-chain enforcement.
- [25 authored Rust regression tests](rust/tests/monotonic_receipt.rs) cover valid synthetic successor, broken predecessor, older head/sequence, regressed revocation epoch, source/issuer ancestry substitution, changed holder, invalid or replayed rotation, rotation authority pin or signature forgery, and locked first-receipt/replay acceptance. **Cargo compilation, test execution and CI results remain unverified.**
- [Neon 4D GitHub Pages-ready lab](211/) retains the 16-vertex/32-edge tesseract and illustrates six synthetic forward-chain decisions. The browser neither executes Rust nor authenticates real remote custody. [Protocol](211/protocol.json) records **Phase XVII 3/8 = 37.5%**, physical qualification **0%**, operational ACT **HOLD**.
- **Limits:** real independent external receipts and rotation authority are unverified; rotation replay policy sets remain supplied instead of independently persisted; receipt and evidence journals use different locks and do not have distributed atomicity. Original physical acquisition remains unobserved and no recovery/physical ACT is authorized.
- **Next AETHER-212-RS:** crash recovery incident proof and ordered two-store reconciliation **without** automatic repair or privilege escalation. `.dlw`

## AETHER-210-RS — Durable local receipt custody and replay screening

- [Native Rust receipt custody store](rust/src/receipt_custody.rs) uses an exclusive Linux process-identity lock, ordered receipt JSON Lines with SHA-256 chaining, expected-head and sequence comparison, file/directory fsync and full readback.
- Each record binds a documentary receipt ID and claimed source locator to the exact AETHER-209 signed anchor digest, holder identity/key fingerprint, custody nonce and declared observation time. Ingestion first screens the anchor against the ledger and authorization registry. Replayed receipt IDs, anchor digests, anchor IDs or custody nonces are rejected across persistent store history.
- [25 authored Rust regression tests](rust/tests/receipt_custody.rs) cover journal readback, persistence across invocations, multiple distinct anchors, duplicate IDs/nonces, stale heads, forged signatures, altered holder pins, torn/corrupted record, rollback, lock contention and fail-closed ACT. Rust test execution and live Pages deployment are **not independently confirmed**.
- [Animated 4D neon Pages laboratory](210/) preserves the 16-vertex and 32-edge tesseract and displays six illustrative receipt errors. The browser cannot create a real durable journal or validate remote custody. [Protocol](210/protocol.json) records **2/8 = 25%**, physical qualification **0%**, ACT **HOLD**.
- **Trust and crash boundary:** the receipt file is a *local copy*, not a separately held remote witness. Its `remote_receipt_sha256` is the submitted anchor-content digest, not independently fetched remote bytes. Its lock is separate from the evidence ledger lock; it cannot make their writes cross-file atomic. A deleted/rolled-back receipt journal can appear empty without an externally held anchor. No real independently authenticated remote receipt or original hardware evidence has been verified; recovery and ACT remain prohibited.
- **Next AETHER-211-RS:** independently sourced, monotonic remote receipt refresh and nonrollback chain, without trusting copied assertions. `.dlw`

## AETHER-209-RS — External anchor observation and joint rollback

- [Native Rust remote anchor verifier](rust/src/remote_anchor.rs) authenticates an ECDSA P-256 signature and exact externally supplied anchor hash, checks predecessor hash, holder fingerprint, declared source/issuer/holder ancestry and replayed anchor identifiers/nonces.
- It examines [local ledger](rust/src/durable_ledger.rs) history at the externally pinned anchor sequence and compares the complete [authorization registry](rust/src/authorization_registry.rs) snapshot hash and revocation epoch. A journal and registry jointly rolled back below the anchor's sequence are rejected even if their *local* hashes remain internally consistent.
- [25 authored Rust regression tests](rust/tests/remote_anchor.rs) challenge joint rollback, valid-prefix truncation, divergent history, registry mutation, changed epoch, signature forgery, shared ancestry, substituted pin, replay and missing authenticated remote custody. Compilation and test execution are **not yet verified**.
- [Animated 4D neon laboratory](209/) retains the rotating tesseract and six synthetic decision scenarios. The browser does not execute Rust, authenticate remote origins or store a real external receipt. [Protocol](209/protocol.json) records **1/8 = 12.5%** documentary progress.
- **HOLD boundary:** no real independent remote custodian or physically witnessed acquisition has been authenticated. The gate's `may_append` and `may_recover` are always false, regardless of signed synthetic evidence. Holder-authentication flags in the caller policy are not independently verified proof.
- A hostile controller can jointly roll back both local files and any *locally controlled* purported external anchor. For useful anti-rollback, the anchor must actually be held outside that ancestry and supplied through an authenticated out-of-band channel. **Next AETHER-210-RS:** custody envelope and persistence for such externally received checkpoint receipts, without inferring external trust from a signature. `.dlw`

**Phase XVII 12.5% · Physical qualification 0% · Operational ACT HOLD.**
