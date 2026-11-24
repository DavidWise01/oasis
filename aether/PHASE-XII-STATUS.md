# AETHER Phase XII — Independent Physical Evidence Admission

**AETHER-173 ORIGINAL BYTE-DIGEST AND HARDWARE-CLOCK ADMISSION CONTRACT COMMITTED. Planned Phase XII software bounds: 5/8 = 62.5%. Empirical physical qualification: 0%. Operational authority: HOLD.**

Phase XI was closed as an eight-turn software protocol sequence by [AETHER-168](168/decision.json); it was **not** physically qualified. Phase XII performs strict intake of independently authenticated original hardware evidence without allowing simulated signatures, synthetically separate credential strings, or shared-root witnesses to count as independent physical observations.

| Turn | Bound | Stage | Phase XII protocol progress |
|---|---|---|---:|
| 1 | 169 Independent Physical Evidence Admission | **ACCEPTED — documentary contract only** | **12.5%** |
| 2 | 170 Original hardware identity challenge | **ACCEPTED — structural simulation only** | **25%** |
| 3 | 171 External reference certificate authentication | **ACCEPTED — synthetic structural certificate audit only** | **37.5%** |
| 4 | 172 Independent ancestry and common-root exclusion | **ACCEPTED — synthetic graph-structure checks only** | **50%** |
| 5 | 173 Original physical acquisition digest and clock | **ACCEPTED — synthetic capture-integrity contract only** | **62.5%** |
| 6 | 174 Same-path response and uncertainty review | Planned | 62.5% |
| 7 | 175 Drift/alarm real trace qualification | Planned | 62.5% |
| 8 | 176 Physical qualification decision / freeze | Planned | 62.5% |

## AETHER-173 — Raw acquisition digest and monotonic hardware clock

- [Byte-integrity verification engine](173/verification.mjs) computes WebCrypto SHA-256 of supplied raw bytes and compares with a declared capture digest; checks challenge nonce, expected device and clock identity, replayed capture ID, total sample count, monotonic hardware-time tags and consecutive sample counters.
- [Negative test suite](173/test.mjs) specifies **16 synthetic cases** for missing bytes, alteration, malformed declared digest, identity/nonce mismatch, clock mismatch, replay, counter discontinuity, clock rollback and untrusted physical source flags. Full byte-identical test execution is **not yet confirmed**; the source has been published.
- [Pages-ready neon laboratory](173/) demonstrates browser-local SHA-256, tampered input, rollback, skipped counter and replay. This is explicitly a mock fixture without physical hardware.
- Hash equality proves only equality of supplied bytes with a supplied digest; it cannot prove hardware source, calibrated clock, acquisition integrity prior to receipt, or independently authenticated origins. The verifier returns only **DOCUMENTARY_REVIEW_ONLY** or **REJECT**, always operational **HOLD**.
- [Protocol JSON](173/protocol.json) records **physical samples 0, physical qualification 0%, Phase XII protocol development 5/8 = 62.5%**, predecessor AETHER-172, and missing hardware trust.
- **Next natural bound AETHER-174:** physical same-path response and uncertainty review. No promotion from model measurements, unverified timestamps or synthetic signatures. `.dlw`

## AETHER-172 — Ancestry graph and shared-origin exclusion

- [Deterministic ancestry gate](172/verification.mjs) resolves original root ancestry by following directed graph links for DUT, REFERENCE, BENCH. Rejects unresolved parents, ancestry cycles, duplicate node IDs, root-with-parent contradictions, orphan derived nodes, duplicate roles, shared device serials, malformed or duplicated capture SHA-256, and every shared-root pair.
- **15/15 local synthetic graph assertions passed**, including three independent common-root pair faults and a deliberately forged assertion of external origin authentication. The forged flag can reach only **DOCUMENTARY_REVIEW_ONLY**; no branch ever grants real-world ACT.
- [Published test suite](172/test.mjs), [protocol](172/protocol.json) and [neon interactive ancestry laboratory](172/) are source-committed. A byte-identical checkout execution and deployed GitHub Pages browser run remain separately unverified.
- **No real physical sample, root genealogy, certificate issuer or instrument provenance is authenticated.** Separate root labels are simulated source claims, never three independently verified physical sources. A graph of declared origins cannot establish the truth of those origins.
- **Phase XII protocol progress: 4/8 = 50%; physical qualification 0%, operational authority HOLD.** Phase XI predecessor record and earlier Phase XII bounds are not overwritten.
- **Next natural bound AETHER-173:** original acquisition bytes, capture digest and monotonic hardware clock, with fail-closed original-source verification. `.dlw`

## AETHER-171 — External reference-certificate chain structural admission

- [Deterministic certificate gate](171/verification.mjs) checks issuer/subject linkage across three levels, serial collisions, self-issuance, timestamp windows, fingerprint format, explicit pinned root, shared-DUT-root exclusion, reference device serial, revocation state and timestamp binding.
- **16/16 local synthetic assertions passed** in an isolated JavaScript execution of the verifier before publication. The [published test suite](171/test.mjs) reproduces 15 negative cases plus one documentary acceptance; a byte-identical GitHub checkout run is not claimed.
- Even with fictional external-verification flags all set true, the verifier returns only **DOCUMENTARY_REVIEW_ONLY** and always **HOLD**; no cryptographic signature, trust anchor, external issuer registry, certificate revocation responder or physical reference instrument has actually been authenticated. Trust booleans are not external evidence.
- [Neon Pages-ready visualization](171/) runs mock browser certificate challenges; [protocol](171/protocol.json) records missing physical inputs and the zero percent physical qualification.
- Phase XII protocol progress **3/8 = 37.5%**; physically authenticated references **0**, original physical samples **0**, operational ACT **HOLD**. No alteration of prior Phase XI freeze or Phase XII bounds.
- **Next AETHER-172** independently resolve complete source ancestry and common-root exclusion, without switching to quorum, a voting regime, or Byzantine consensus. `.dlw`

## AETHER-170 — Original instrument identity structural challenge

- [Identity challenge verification module](170/verification.mjs) implements deterministic checks for missing fields, expected challenge/nonce/serial binding, signed-response field presence, fresh time windows, nonce replay, and original capture digest format. These are **structural checks only**.
- [Protocol contract](170/protocol.json) fixes eight independent physical prerequisites and the operational **HOLD**. [Standalone test program](170/test.mjs) defines 12 synthetic assertions; **test execution is not independently confirmed**.
- [Neon HTML laboratory](170/) imports the verification module and can run synthetic browser demonstrations. Its visible outcome cannot grant physical authority.
- Even when structural fields appear valid, manufacturer identity, source possession, external registry and original physical capture require trustworthy independent verification. Browser-supplied flags are not authenticators; the module never emits real ACT.
- **Phase XII 2/8 = 25% planned software protocol progress, physical qualification 0%, authenticated original instrument challenges 0; operational authority HOLD.** No real DUT, manufacturer key, trusted remote registry, reference certificate or original instrument data was obtained.
- **Next bound AETHER-171:** externally authenticated independent reference certificate provenance. Exclude shared-root and self-issued certificates; no promotion on missing authority records. `.dlw`

## AETHER-169 — Fail-closed physical evidence intake boundary

- [Machine-readable original physical admission contract](169/admission.json) has **eight missing evidence requirements**: DUT hardware identity, independent reference, independent bench, independent origin ancestry, original raw acquisition, same-path physical response, physical drift/alarm trace, and traceable measurement uncertainty.
- [Read-only HTML admission laboratory](169/) illustrates eight unfilled requirements. Its local JSON check verifies **document consistency only**, not device presence, real-source authenticity, actual certificate validity, instrument calibration, or physical independence.
- **Operational authority remains HOLD, physical qualification remains 0%, original physical samples zero.** Missing physical evidence is a veto. No simulated MAC, mock signature, synthetic token, quorum, or manufactured source count can satisfy the physical admission gate.
- Source hashes and physical HOLD of the prior Phase XI freeze are preserved. This Phase XII tracker is a new append-only document, not a rewrite of the archived Phase XI record.
- GitHub commit publication and source readback can establish published code, but not live Pages execution or physical authority. Those claims require separate verification.
- **Next natural bound:** AETHER-170, original physical device identity challenge; independently established hardware possession, manufacturer-verifiable serial, authenticated physical time/challenge evidence, and anti-replay handling, all fail closed when missing.

**Invariant 169:** a source claim is not an independent observation; evidence completeness is not evidence authenticity. `.dlw`
