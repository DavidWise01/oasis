# AETHER Phase XIII — Physical Evidence Escrow and Source Custody

**AETHER-180 DUAL ECDSA P-256 TRANSFER/RECEIPT COUNTERSIGNATURE GATE COMMITTED. Phase XIII: 4/8 = 50% software protocol coverage. Physical qualification 0%. Operational authority HOLD.**

Phase XII closed at 8/8 software bounds through [AETHER-176](176/decision.json), explicitly **without physical qualification**. All past freezes remain historical records. Phase XIII tracks software protocols for acquiring and protecting evidence from genuinely independent original physical sources; no synthetic receipt, signature-shaped string, or declared root label qualifies as physical data.

| Turn | Bound | Software protocol state | Progress |
|---|---|---|---:|
| 1 | 177 Physical evidence escrow and custody | **ACCEPTED — synthetic structural gate only** | **12.5%** |
| 2 | 178 Byte-exact sealed capture manifest | **ACCEPTED — synthetic byte-integrity audit only** | **25%** |
| 3 | 179 Authenticated custodian identity and signatures | **ACCEPTED — cryptographic mock-key signature gate only** | **37.5%** |
| 4 | 180 Independent transfer and receipt countersignature | **ACCEPTED — synthetic dual-key cryptographic gate only** | **50%** |
| 5 | 181 Clock, source and challenge provenance escrow | Planned | 50% |
| 6 | 182 External archive replication and tamper detection | Planned | 50% |
| 7 | 183 Blind original physical evidence admission review | Planned | 50% |
| 8 | 184 Phase XIII qualification decision and freeze | Planned | 50% |

## AETHER-180 — Dual-signed transfer and receipt countersignature

- [Verifier](180/verification.mjs) performs genuine P-256 ECDSA verification against distinct sender and receiver public keys over fixed-order canonical transfer and receipt records. The receiver's signed receipt binds the sender's SHA-256 transfer digest, capture digest, custodian roles, challenge and transfer ID; detects duplicate IDs, altered evidence, time reversal, missing or delayed receipts, revoked or unauthorized keys and broken predecessors.
- [24-case test suite](180/test.mjs) is published with genuine WebCrypto key generation and signatures, tampering, replay, signature forgery, revoked keys, authorization checks, receipt mismatch and a fully flagged synthetic trust scenario. **Test execution has not been independently confirmed in this turn; no 24/24 runtime-pass claim is made.**
- [Full 4D neon laboratory](180/) retains the rotating 16-vertex, 32-edge cyan/blue/violet tesseract with ghost shadow, interactive orbit controls and dual-signature custody fault injections. Live GitHub Pages deployment/browser test is unverified.
- [Protocol contract](180/protocol.json): **Phase XIII 4/8 = 50%**, zero real physical samples, physical qualification 0%, authority HOLD. Two valid signatures under locally constructed test keys do not establish two authenticated real people, independent original hardware origins or physical possession.
- Previous records AETHER-176 through AETHER-179 are preserved unchanged. Next bound **AETHER-181: clock, source and challenge provenance escrow**. `.dlw`

## AETHER-179 — Canonical signed custody event & claimed custodian identity

- [ECDSA P-256 WebCrypto verifier](179/verification.mjs) verifies a real cryptographic signature over fixed-order canonical custody JSON, using the public key from an explicit registry record. Checks key/custodian binding, permitted action, declared revocation and validity windows, challenge, event ID replay, capture digest format and time policy.
- The [18-case synthetic regression suite](179/test.mjs) covers valid signatures, tampering, altered signatures, registry mismatches, revoked/disallowed/expired keys, replay, invalid capture ancestry fields and physical origin authentication gaps. **The test suite has been published, but a byte-identical Node.js checkout execution has not been independently verified in this session.**
- [Full 4D neon laboratory](179/) retains the 16-vertex 32-edge rotating cyan/violet shadow tesseract with pause, orbit and shadow toggles. The browser creates an **ephemeral synthetic private key**, signs a canonical event and demonstrates real WebCrypto verification plus forged and tampered cases.
- The registry is a **locally supplied mock registry**, not an externally authenticated custodian identity provider. Signature validity only proves possession of a matching key; browser flags cannot prove an independent source, physical receipt or actual physical action. Cryptographic signature success always yields at most DOCUMENTARY_REVIEW_ONLY; there is **no ACT pathway**.
- [Protocol contract](179/protocol.json): **Phase XIII 3/8 = 37.5%**, original physical samples 0, physical qualification 0%, operational HOLD. No preceding freeze or phase bound is overwritten.
- **Next AETHER-180:** independently bound transfer/receive countersignatures and receipt continuity, still requiring external identity and genuine original physical evidence. `.dlw`

## AETHER-178 — Byte-exact original capture and canonical manifest escrow

- [Verifier](178/verification.mjs) uses WebCrypto SHA-256 over actual supplied Uint8Array capture bytes, recomputes a second SHA-256 over fixed-field-order canonical UTF-8 JSON, and checks length, schema, instrument/challenge identity, declared source ancestry, capture ID replay, sequence/genesis/predecessor references and seal timestamp form.
- **20/20 local Node.js WebCrypto synthetic checks passed**. Tests cover missing/empty bytes, byte tampering, changed metadata, length errors, replay, identity/challenge mismatch, shared DUT origin, bad digests, malformed timestamp, invalid genesis/sequence/predecessor and unauthenticated physical origin, custody and acquisition. Even a fully flagged synthetic case remains DOCUMENTARY_REVIEW_ONLY and cannot authorize ACT. [Published tests](178/test.mjs) have not been independently replayed from GitHub checkout.
- [Full 4D neon HTML lab](178/) projects a 16-vertex 32-edge rotating tesseract with cyan-blue and violet shadow, plus six synthetic capture integrity scenarios, pause/slow/shadow controls and four-stage byte-digest-manifest-HOLD visualization. Browser/Pages execution remains unverified.
- [Protocol contract](178/protocol.json) explicitly retains zero original physical samples, physical qualification 0% and operational HOLD. SHA-256 detects altered received bytes and manifest fields, but **cannot independently prove instrument source, original acquisition, custody identity or signatures**.
- **Phase XIII 2/8 = 25%.** The AETHER-176 Phase XII decision and AETHER-177 evidence remain untouched.
- **Next AETHER-179:** real custodian identity and verifiable digital signatures over canonicalized custody events, with trusted roots externally established; mock signatures must never grant physical authority. `.dlw`

## AETHER-177 — Physical evidence escrow chain-of-custody structural gate

- [Custody verification module](177/verification.mjs) checks genesis acquisition, monotonic timestamps, sequential counters, mandatory custody fields, origin claims, acquisition challenge binding, linked predecessor digests, capture consistency, transfer/receive custody match, duplicated receipts and seal closure.
- **25/25 local in-process synthetic assertions passed.** Includes capture substitution, forged self-origin, clock rollback, duplicate receipt, broken predecessor links, missing transfer receipt and a simulated fully trusted fixture that still cannot grant real physical authorization. [Published test module](177/test.mjs) is suitable for independent Node.js checkout execution, which has not yet been confirmed.
- [Escrow contract](177/protocol.json) explicitly records no physical samples and HOLD, plus missing trusted signatures and physical custody. SHA-256-shaped strings are tested for formatting and predecessor linkage, **not cryptographically recalculated over canonical custody events**. This limitation precludes any claim of cryptographic tamper proof.
- [Full 4D shadow tesseract HTML laboratory](177/) includes 16 vertices, 32 edges, 4D rotation and perspective projection, cyan/violet double shadow, responsive neon instrumentation and six fault-injection scenarios. This is a synthetic diagnostic visualization, not hardware evidence.
- **Physical qualification 0%; independent real original evidence samples 0; operational ACT HOLD.** Prior Phase XII freeze and other bounds remain untouched.
- Next natural bound: **AETHER-178** byte-exact original capture escrow with canonical SHA-256 manifest verification and immutable receipt references; physical origin remains unverified until externally authenticated.

**Invariant 177:** A chain of declared custody does not itself authenticate the original physical acquisition. .dlw
