# AETHER Phase XIII — Physical Evidence Escrow and Source Custody

**AETHER-178 BYTE-EXACT CAPTURE/MANIFEST SOFTWARE GATE PASSED 20/20 LOCAL SYNTHETIC CHECKS. Phase XIII: 2/8 = 25% software protocol coverage. Physical qualification 0%. Operational authority HOLD.**

Phase XII closed at 8/8 software bounds through [AETHER-176](176/decision.json), explicitly **without physical qualification**. All past freezes remain historical records. Phase XIII tracks software protocols for acquiring and protecting evidence from genuinely independent original physical sources; no synthetic receipt, signature-shaped string, or declared root label qualifies as physical data.

| Turn | Bound | Software protocol state | Progress |
|---|---|---|---:|
| 1 | 177 Physical evidence escrow and custody | **ACCEPTED — synthetic structural gate only** | **12.5%** |
| 2 | 178 Byte-exact sealed capture manifest | **ACCEPTED — synthetic byte-integrity audit only** | **25%** |
| 3 | 179 Authenticated custodian identity and signatures | Planned | 25% |
| 4 | 180 Independent transfer and receipt countersignature | Planned | 25% |
| 5 | 181 Clock, source and challenge provenance escrow | Planned | 25% |
| 6 | 182 External archive replication and tamper detection | Planned | 25% |
| 7 | 183 Blind original physical evidence admission review | Planned | 25% |
| 8 | 184 Phase XIII qualification decision and freeze | Planned | 25% |

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
