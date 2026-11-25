# AETHER Phase XVII — External Recovery Anchors and Independently Held Evidence

**AETHER-209-RS EXTERNALLY PINNED REMOTE ANCHOR SCREENING COMMITTED. Phase XVII documentary software progress 1/8 = 12.5%. Authenticated remote receipts: 0. Authenticated original physical captures: 0. Physical qualification: 0%. Operational ACT: HOLD.**

Phase XVI's [AETHER-208 freeze](208/decision.json) remains unchanged, with 8/8 software milestones closed but original physical evidence, independent remote custody, and runtime certification unresolved. A locally valid journal and registry can be rolled back together; Phase XVII examines the need for externally anchored history and independently adjudicated recovery.

| Turn | Milestone | State | Progress |
|---|---|---|---:|
| 1 | 209 Remote-anchor verifier and joint-rollback screening | **COMMITTED — synthetic signed anchor and ledger/registry comparison** | **12.5%** |
| 2 | 210 Independent anchor-receipt custody envelope and durable replay | Planned | 12.5% |
| 3 | 211 Signed external-receipt refresh and nonrollback chain | Planned | 12.5% |
| 4 | 212 Crash recovery incident proof without automatic repair | Planned | 12.5% |
| 5 | 213 Independently retained control-ancestry evidence | Planned | 12.5% |
| 6 | 214 Cross-host receipt-consistency and equivocation screening | Planned | 12.5% |
| 7 | 215 Adversarial remote custody and recovery qualification | Planned | 12.5% |
| 8 | 216 Phase XVII documentary software freeze | Planned | 12.5% |

## AETHER-209-RS — External anchor observation and joint rollback

- [Native Rust remote anchor verifier](rust/src/remote_anchor.rs) authenticates an ECDSA P-256 signature and exact externally supplied anchor hash, checks predecessor hash, holder fingerprint, declared source/issuer/holder ancestry and replayed anchor identifiers/nonces.
- It examines [local ledger](rust/src/durable_ledger.rs) history at the externally pinned anchor sequence and compares the complete [authorization registry](rust/src/authorization_registry.rs) snapshot hash and revocation epoch. A journal and registry jointly rolled back below the anchor's sequence are rejected even if their *local* hashes remain internally consistent.
- [25 authored Rust regression tests](rust/tests/remote_anchor.rs) challenge joint rollback, valid-prefix truncation, divergent history, registry mutation, changed epoch, signature forgery, shared ancestry, substituted pin, replay and missing authenticated remote custody. Compilation and test execution are **not yet verified**.
- [Animated 4D neon laboratory](209/) retains the rotating tesseract and six synthetic decision scenarios. The browser does not execute Rust, authenticate remote origins or store a real external receipt. [Protocol](209/protocol.json) records **1/8 = 12.5%** documentary progress.
- **HOLD boundary:** no real independent remote custodian or physically witnessed acquisition has been authenticated. The gate's `may_append` and `may_recover` are always false, regardless of signed synthetic evidence. Holder-authentication flags in the caller policy are not independently verified proof.
- A hostile controller can jointly roll back both local files and any *locally controlled* purported external anchor. For useful anti-rollback, the anchor must actually be held outside that ancestry and supplied through an authenticated out-of-band channel. **Next AETHER-210-RS:** custody envelope and persistence for such externally received checkpoint receipts, without inferring external trust from a signature. `.dlw`

**Phase XVII 12.5% · Physical qualification 0% · Operational ACT HOLD.**
