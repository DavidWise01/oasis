# AETHER Phase XIV — Original External Evidence Intake and Custody Onboarding

**AETHER-187 ORIGINAL-BYTE CUSTODY & EXTERNAL VERIFIER SIGNATURE GATE COMMITTED. Phase XIV software-protocol progress: 3/8 = 37.5%. Authenticated original physical captures: 0. Physical qualification: 0%. Operational authority: HOLD.**

Phase XIII [AETHER-184](184/decision.json) was closed as an eight-bound documentary software protocol; no physically authenticated independent source was admitted. Phase XIV introduces original external evidence intake contracts without treating mock external issuers, signed keys, or synthetic bundles as physical proof.

| Turn | Planned bound | Status | Software progress |
|---|---|---|---:|
| 1 | 185 Original acquisition receipt and custody onboarding | **COMMITTED — synthetic intake cryptography only** | **12.5%** |
| 2 | 186 External issuer identity and manufacturer anchor | **COMMITTED — synthetic certificate chain only** | **25%** |
| 3 | 187 Original acquisition byte custody with external verifier | **COMMITTED — synthetic dual-signature custody gate only** | **37.5%** |
| 4 | 188 Physical instrument, clock and challenge binding | Planned | 37.5% |
| 5 | 189 Independent custodian and transfer receipt authentication | Planned | 37.5% |
| 6 | 190 Blind external-source physical replay audit | Planned | 37.5% |
| 7 | 191 Original physical response and alarm qualification | Planned | 37.5% |
| 8 | 192 Phase XIV documentary qualification decision and freeze | Planned | 37.5% |

## AETHER-187 — Original-byte custody with independent-verifier signature

- [Verifier](187/verification.mjs) computes real SHA-256 over supplied raw Uint8Array bytes, validates P-256 ECDSA signatures for an acquisition receipt and separate verifier receipt, and binds verifier signature to the canonical acquisition and custody SHA-256 digests. Checks anti-replay, time ordering, challenge, device serial, independent claimed ancestry, distinct operator/administrator, key revocation and receipt integrity.
- [27-case synthetic regression suite](187/test.mjs) includes byte tampering, capture substitution, changed custody receipt, forged acquisition/verifier signature, replay, shared root ancestry, shared operator/administrator, incomplete receipts and trust-flag spoofing. **The suite is authored and committed; execution from checkout has not been independently confirmed.**
- [Full 4D neon laboratory](187/) preserves the rotating 16-vertex 32-edge cyan/blue/violet shadow-tesseract and adds fault injection for capture corruption, changed custody, shared root/operator and forged verifier. Pages deployment and live Chromium execution are unverified.
- [Protocol](187/protocol.json) records **Phase XIV 3/8 = 37.5%**, original externally authenticated physical captures **0**, physical qualification **0%**, operational ACT **HOLD**.
- Separate synthetic public keys and declarative root labels cannot establish real-world independent physical provenance. The custody handoff is digest-bound, but is not separately countersigned in this bound. A client-supplied trust map cannot authorize ACT.
- Previous AETHER-184 through 186 records remain unchanged. **Next AETHER-188:** original instrument / calibrated clock / challenge binding with physical-source authenticity unresolved. `.dlw`

## AETHER-186 — External issuer identity and manufacturer anchor gate

- [ECDSA P-256 trust-chain verifier](186/verification.mjs) checks a pinned root key fingerprint, root-signed manufacturer CA, CA-signed instrument issuer, issuer-signed acquisition receipt, key roles/permissions, revocation claims, validity windows, acquisition challenge and instrument serial binding.
- [22-case synthetic regression suite](186/test.mjs) was committed, with valid chain, tampered certificates and receipts, altered issuer identity, revoked/expired certificates, unpinned roots, stale receipt and synthetic trust-flag escalation. **The committed suite has not been executed in a Node.js checkout in this turn.**
- [Full 4D neon shadow-tesseract laboratory](186/) retains the cyan/violet rotating 16-vertex, 32-edge geometry with 3D perspective, double shadow projection and motion controls. Six certificate trust fault buttons use synthetic P-256 keys. Live browser and GitHub Pages deployment remain unverified.
- This is a **custom synthetic certificate schema, not X.509**. A locally pinned key and matching signatures are not external verification of a real manufacturer root, issuer identity or physical instrument.
- [Protocol](186/protocol.json): **Phase XIV 2/8 = 25%**, authenticated original physical captures **0**, physical qualification **0%**, operational ACT **HOLD**. A client-controlled trust registry is never grounds to enable ACT.
- Phase XIII and AETHER-185 historical records are unchanged. **Next AETHER-187:** original acquisition byte custody with an independently authenticated external verifier. `.dlw`

## AETHER-185 — Original external evidence acquisition receipt

- [Verification engine](185/verification.mjs) performs genuine WebCrypto SHA-256 over supplied original byte arrays and ECDSA P-256 verification of a canonical acquisition receipt against a separately supplied issuer registry key. It checks source serial and origin, challenge equality, package and intake replay, receipt time policy, declared byte length, key revocation and issuer ancestry.
- [24-case synthetic test suite](185/test.mjs) exercises missing bytes, capture mutation, forged signatures, replayed package, wrong challenge/device, stale/future receipts, revoked issuers, self-issued roots and all four missing external trust conditions. **Test execution has not yet been confirmed from a GitHub checkout; this is a published suite, not a 24/24 runtime-pass claim.**
- [Full 4D neon Pages-ready HTML lab](185/) retains the 16-vertex, 32-edge rotating cyan/blue/violet tesseract and offset shadow projection, motion controls and six browser fault-injection scenarios. Browser and Pages execution remain unverified.
- [Protocol contract](185/protocol.json) preserves **physical qualification 0%** and **ACT HOLD**, irrespective of mock-key signature or locally asserted trust flags. No actual original externally verified physical capture has been supplied. A valid signature authenticates possession of a key, not an independent physically validated issuer.
- Historical AETHER-184 and all preceding records remain unchanged. **Next AETHER-186:** independently authenticated issuer identity, manufacturer credential anchors and trust-root ancestry; physical ACT remains HOLD without real evidence. `.dlw`
