# AETHER Phase XIV — Original External Evidence Intake and Custody Onboarding

**AETHER-191 RUST PHYSICAL-RESPONSE AND ALARM-EVIDENCE SCREENING COMMITTED. Phase XIV software-protocol progress: 7/8 = 87.5%. Authenticated original physical captures: 0. Physical qualification: 0%. Operational authority: HOLD.**

Phase XIII [AETHER-184](184/decision.json) was closed as an eight-bound documentary software protocol; no physically authenticated independent source was admitted. Phase XIV introduces original external evidence intake contracts without treating mock external issuers, signed keys, or synthetic bundles as physical proof.

| Turn | Planned bound | Status | Software progress |
|---|---|---|---:|
| 1 | 185 Original acquisition receipt and custody onboarding | **COMMITTED — synthetic intake cryptography only** | **12.5%** |
| 2 | 186 External issuer identity and manufacturer anchor | **COMMITTED — synthetic certificate chain only** | **25%** |
| 3 | 187 Original acquisition byte custody with external verifier | **COMMITTED — synthetic dual-signature custody gate only** | **37.5%** |
| 4 | 188 Physical instrument, clock and challenge binding | **COMMITTED — synthetic signed calibration and acquisition gate only** | **50%** |
| 5 | 189 Independent custodian and transfer receipt authentication | **COMMITTED — synthetic dual-custodian handoff gate only** | **62.5%** |
| 6 | 190 Blind external-source physical replay audit | **COMMITTED — synthetic blind replay and ancestry audit only** | **75%** |
| 7 | 191 Original physical response and alarm qualification | **COMMITTED — Rust synthetic response/alarm gate only** | **87.5%** |
| 8 | 192 Phase XIV documentary qualification decision and freeze | Planned | 87.5% |

## Rust migration — AETHER-RS-001 (2026-11-25)

- **Rust source committed:** [aether/rust](rust/) introduces native Rust 2021 `aether-evidence` crate with actual SHA-256 byte hashing, P-256 ECDSA raw-signature verification, blinded AETHER-190 capture schema, separate caller-supplied source/verifier registries, challenge nonce/replay and shared-ancestry checks. Applicant names are excluded from the canonical review record.
- [Rust integration tests](rust/tests/blind_replay.rs) contain **23 source-level tests**, including valid synthetic signatures, byte substitution, signature forgery, duplicate trial/capture/challenge, shared operator/admin/root/source ancestry, missing registry, and immutable physical HOLD.
- [GitHub Actions workflow](../.github/workflows/aether-rust.yml) installs stable Rust and runs formatting normalization, Clippy and Cargo tests on push/PR/manual dispatch. **No Rust toolchain was available in this assistant environment; test execution and GitHub Actions result are not yet verified.**
- The existing AETHER-185–190 JavaScript source and GitHub Pages 4D labs are preserved unchanged. Future verification work can use Rust; browser integration requires a separate compiled WebAssembly bridge.
- This is a software-language migration, **not a new Phase XIV bound**: software phase progress remains **6/8 = 75%**, physical qualification **0%**, ACT **HOLD**. `.dlw`

## AETHER-191-RS — Original physical response and alarm documentary screening

- [Native Rust alarm verifier](rust/src/alarm.rs) binds original capture SHA-256 and P-256 signature verification to claimed device/reference identity, acquisition nonce, calibration digest, separately declared roots, reported response and tolerance, issued-alarm event and acknowledgement timestamps. It detects replay, substitutions and excessive observation/issuance/acknowledgement delays.
- [28 authored Rust integration tests](rust/tests/alarm_response.rs) cover signed synthetic baseline, false trust escalation, capture substitution, signature forgery, device/reference switching, challenge/capture mismatch, alarm replay, missing ACK, tolerance failure, alarm chronology and authentication failures. **Runtime execution and GitHub Actions success have not been independently verified.**
- [Full 4D neon HTML dashboard](191/) retains the rotating cyan/blue/violet tesseract and shadow with six illustrative alarm scenarios. The browser visualization explicitly does **not** execute Rust or assert actual hardware observation. Future WASM integration would be a separate task.
- [Protocol](191/protocol.json) records **Phase XIV 7/8 = 87.5%** of documentary software milestones. Real authenticated physical source captures **0**, physical qualification **0%**, operational **HOLD**.
- All preceding AETHER-184–190 records remain intact. **Next AETHER-192-RS:** close Phase XIV with a Rust-validated documentary decision and evidence freeze, never authorizing ACT absent original independent physical evidence. `.dlw`

## AETHER-190 — Blind external-source replay audit

- [Verifier](190/verification.mjs) reviews three capture records without using applicant names, recomputes actual SHA-256 from supplied bytes, validates each ECDSA P-256 capture signature against separately supplied synthetic source registry keys, and checks duplicate capture/trial IDs, reused challenge nonces, declared physical-source ancestry, operator/admin/root collisions and verifier provenance conflicts.
- [28-case synthetic regression suite](190/test.mjs) covers malformed capture entries, duplicate nonce/trial/capture, bytes tampering, forged signatures, missing root registry, shared operator and physical-source ancestry, and synthetic trust flag spoofing. **Published but independently executed Node.js checkout not yet confirmed.**
- [Full neon 4D shadow-tesseract lab](190/) preserves the animated 16-vertex / 32-edge cyan, blue and violet hypercube with perspective, moving shadow and motion controls, plus six browser fault-injection scenarios. Live browser and Pages deployment remain unverified.
- [Protocol](190/protocol.json): **Phase XIV 6/8 = 75%**, authenticated original physical captures **0**, physical qualification **0%**, operational ACT **HOLD**. Synthetic registry labels, valid signatures and distinct software handles do not establish actual physical independence.
- Earlier Phase XIII freeze and AETHER-185–189 records remain unchanged. **Next AETHER-191:** original physical response and alarm qualification with physically observed device behavior and traceable independent calibration required. `.dlw`

## AETHER-189 — Independent custodian identity and countersigned receipt gate

- [Verifier](189/verification.mjs) validates real ECDSA P-256 signatures over exact canonical sender transfer and receiver receipt, computes handoff SHA-256, and requires receipt binding to the original capture identity and digest. Checks anti-replay, transfer/receipt chronology, predecessor continuity, local public-key root fingerprint pins, key permissions, revocation and distinct declared ancestry roots, operators and administrators.
- [30-case synthetic suite](189/test.mjs) was committed. It exercises altered receipts, forged sender/receiver signatures, replay, missing identities, revoked credentials, shared root/operator/administrator and false physical-attestation flags. **The published suite has not been executed from a GitHub checkout in this turn; no 30/30 runtime result is asserted.**
- [Full 4D neon Pages-ready laboratory](189/) retains the rotating 16-vertex / 32-edge cyan-blue-violet shadow tesseract and animation controls, with six handoff fault-injection buttons. Live Pages deployment and Chromium execution remain unverified.
- [Protocol](189/protocol.json) records **Phase XIV 5/8 = 62.5%**, externally authenticated original physical samples **0**, physical qualification **0%**, and operational authority **HOLD**. Locally pinned test roots and two independent software keys are not real authenticated custodians or real physical handoff proof.
- Previous Phase XIII freeze and AETHER-185–188 records are unchanged. **Next AETHER-190:** blind external-source physical replay audit with duplicate ancestry rejection and original hardware evidence requirements. `.dlw`

## AETHER-188 — Signed instrument, calibration, clock and challenge binding

- [Verifier](188/verification.mjs) checks the two genuine WebCrypto ECDSA P-256 signatures over canonical calibration and capture records, computes SHA-256 over original supplied bytes, binds the calibration record digest into the capture, and checks challenge freshness/replay, instrument/clock serials, sample counters, nonmonotonic ticks, calibration validity and bounded clock interval claims.
- [29-case synthetic test suite](188/test.mjs) covers byte substitution, swapped instruments or clocks, expired challenge and calibration, tick rollback and counter discrepancies, altered calibration, forged or revoked keys, shared calibrator/device operator and client-driven trust-flag escalation. **Tests committed but execution from an independent GitHub checkout remains unverified.**
- [Full 4D neon Pages-ready laboratory](188/) preserves the 16-vertex, 32-edge cyan/blue/violet rotating shadow tesseract and motion controls, adding interactive clock rollback, instrument substitution, expired challenge, altered calibration and forged-capture scenarios.
- [Protocol](188/protocol.json) records **Phase XIV 4/8 = 50%**, original externally authenticated physical captures **0**, physical qualification **0%**, operational ACT **HOLD**. Synthetic clock and calibration signatures cannot establish real hardware traceability, physical clock calibration or physical acquisition truth.
- The preceding Phase XIII freeze and AETHER-185–187 files remain unchanged. **Next AETHER-189:** real custodian identity and countersigned transfer receipt authentication under separate roots. `.dlw`

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
