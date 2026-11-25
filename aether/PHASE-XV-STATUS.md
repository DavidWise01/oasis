# AETHER Phase XV — Original Physical Evidence Acquisition in Rust

**AETHER-196-RS SIGNED CUSTODY EXPORT AND RECEIVER COUNTERSIGNATURE GATE COMMITTED. Phase XV software protocol: 4/8 = 50%. Authenticated original physical captures: 0. Physical qualification: 0%. Operational authority HOLD.**

The Phase XIV documentary protocol [closed at AETHER-192](192/decision.json), with 8/8 software milestones and **no independently verified original physical measurements or alarms**. Phase XV moves the native Rust code toward ingestion of externally supplied acquisition evidence. Neither synthetic fixtures nor locally assigned source roles may create a physical qualification.

| Turn | Planned bound | State | Progress |
|---|---|---|---:|
| 1 | 193 Rust original-byte physical acquisition intake | **COMMITTED — synthetic Rust structural and signature gate only** | **12.5%** |
| 2 | 194 Out-of-band manufacturer / calibration authority credential import | **COMMITTED — synthetic pinned-credential gate only** | **25%** |
| 3 | 195 Real instrument challenge acquisition receipt and anti-replay | **COMMITTED — synthetic signed acquisition replay gate only** | **37.5%** |
| 4 | 196 Original acquisition secure custody export and independent holder | **COMMITTED — synthetic dual-signature custody gate only** | **50%** |
| 5 | 197 Traceable calibration and physical timing uncertainty | Planned | 50% |
| 6 | 198 External blinded verifier record and ancestry authentication | Planned | 50% |
| 7 | 199 Physical response and alarm original observation qualification | Planned | 50% |
| 8 | 200 Phase XV documentary qualification freeze and physical ACT gate | Planned | 50% |

## AETHER-196-RS — Signed custody export and receiver receipt

- [Native Rust verifier](rust/src/custody_export.rs) binds exported original byte SHA-256, source capture receipt, predecessor hash, sender-signed manifest and receiver-signed receipt. Independent claimed ancestry, revoked keys, duplicate export/receipt/nonce and time ordering are checked.
- [32 authored tests](rust/tests/custody_export.rs) include source-byte substitution, signature forgery, ancestry collisions, replay, altered sequence and swapped receiver. Tests were committed; execution remains unverified.
- [4D neon Pages-ready laboratory](196/) retains the rotating 16-vertex, 32-edge shadow tesseract and illustrative faults. Live Pages unverified; no Rust executes in browser.
- [Protocol](196/protocol.json): **Phase XV 4/8 = 50%**, original authenticated physical captures **0**, physical qualification **0%**, ACT **HOLD**.
- A countersignature is not independently observed possession. Durable atomic replay-ledger persistence and independent physical custody remain unverified. Previous bounds unchanged.
- **Next AETHER-197-RS:** traceable calibration and physical timing uncertainty. `.dlw`

## AETHER-195-RS — Signed acquisition challenge, capture receipt and replay screening

- [Rust challenge module](rust/src/challenge.rs) verifies ECDSA P-256 signatures from the challenge authority and device signing key, a captured-payload SHA-256, an exact challenge record SHA-256 sealed into the receipt, and device/nonce identity, chronology and bounded capture latency. It also checks challenge ID, nonce, capture ID and payload digest against supplied prior history.
- [28 authored Rust integration tests](rust/tests/challenge_receipt.rs) cover document consistency, valid synthetic signatures, altered bytes, stale/expired/future captures, signature forgery, challenge substitution, duplicates against replay history and false trust-flag escalation. **Cargo/CI execution not independently confirmed.**
- [Full 4D neon Pages-ready lab](195/) retains the 16-vertex/32-edge rotating cyan-blue-violet hypercube and projected shadow, adding illustrative replay, forgery, timing and ledger fault buttons. The browser does not execute Rust.
- [Protocol](195/protocol.json) records **Phase XV 3/8 = 37.5%**, original authenticated physical samples **0**, physical qualification **0%**, operational ACT **HOLD**.
- The Rust evaluator emits *proposed ledger identifiers* only after a documentary pass. **Atomic append-only persistence, real hardware capture, externally authenticated signing keys and independent physical calibration remain missing.** A caller-supplied ledger cannot authenticate its own history.
- Previous AETHER-193 and AETHER-194 records and Phase XIV freeze remain unchanged. **Next AETHER-196-RS:** secure custody export and independently authenticated receiving holder. `.dlw`

## AETHER-194-RS — Manufacturer and calibration authority credential import

- [Native Rust signed credential verifier](rust/src/credentials.rs) checks separate manufacturer-device-issuer and calibration-authority ECDSA P-256 signatures over ordered, custom-schema JSON credentials, with two independently declared root pins, usage/role/identity permissions, dates, revocation lists, and root ancestry/operator controls.
- [28 authored Rust integration tests](rust/tests/credential_import.rs) cover successful synthetic signatures, root-pin substitution, forged or revoked certificates, expired signing rights, self-issued identity, permission mismatch and false authority flags. **No local Rust toolchain was available; Cargo or GitHub Actions execution was not verified.**
- [Full 4D neon HTML laboratory](194/) retains the 16-vertex, 32-edge cyan-blue-violet tesseract shadow, motion controls, and interactive illustrative credential failures. This browser dashboard **does not run native Rust**.
- [Protocol](194/protocol.json) records **Phase XV 2/8 = 25%**, original independently authenticated hardware captures **0**, physical qualification **0%**, operational ACT **HOLD**.
- The two pinned mock roots remain *synthetic trust assumptions*. A certificate signature or applicant-controlled root pin does not independently authenticate a manufacturer, a qualified calibration laboratory, or real physical source custody. The custom credential format is **not** a full X.509 trust-chain implementation.
- Earlier Phase XIV closure and AETHER-193 remain unmodified. **Next AETHER-195-RS:** instrument challenge acquisition receipt and anti-replay with externally established source identity required. `.dlw`

## AETHER-193-RS — Original physical acquisition intake (software contract only)

- [Rust intake verifier](rust/src/intake.rs) checks real SHA-256 for supplied capture bytes, an ECDSA P-256 signed canonical record, known instrument serial, one-use challenge identifier and nonce, monotonic challenge/acquisition/expiry timing, calibration SHA-256 binding, bounded upload size, replay history, distinct declared custody ancestry, issuer revocation and policy-controlled public-key identity.
- [26 authored Rust integration tests](rust/tests/original_intake.rs) cover raw bytes, altered captures, replayed nonce and capture IDs, wrong device or calibration, expired challenge, forged signature, missing issuer, shared custody ancestry and missing external authentication. **The tests were committed; successful Cargo/CI execution is not independently confirmed.**
- [4D neon HTML laboratory](193/) retains the rotating 16-vertex, 32-edge cyan-blue-violet 4D tesseract with shadow projection and interactive illustrative faults. It does not run compiled Rust or establish physical device identity.
- [Protocol](193/protocol.json) records **Phase XV 1/8 = 12.5%**, authenticated original physical samples **0**, physical qualification **0%**, and operational ACT **HOLD**, irrespective of synthetic flags.
- All Phase XIV freeze records and earlier AETHER bounds are preserved without modification. **Next AETHER-194-RS:** out-of-band manufacturer and traceable calibration authority credential import. Merely supplying a key or certificate-shaped file cannot authenticate its issuing root. `.dlw`
