# OASIS / KET / ASTROPHAGE — RC1 operator-attested finalization

**Record ID:** `KET-OBF2-RC1-20261014-OPERATOR`
**Date:** 2026-10-14 (America/Chicago)
**Status:** **SOFTWARE RELEASE CANDIDATE FINALIZED; FIELD PASS OPERATOR-REPORTED; PHYSICAL-DEVICE CERTIFICATION NOT YET INDEPENDENTLY VERIFIED**
**Scope:** `{{i}}` identity, `{{d}}` lossless carrier, OBS dual rail, ASTROPHAGE OBF2, Ed25519 sender authentication, TLS 1.3 mutual authentication, single-writer fsync-before-ACK receipt journal, and Confluence observer interface.

## Operator declaration and evidence quality

On 2026-10-14 the project operator reported: **"it passed, certify and finalize please"** in response to the remaining Gate 6 acceptance work.

This is recorded as **operator-reported PASS**. No `FINAL_RESULT.json` from the Windows/QEMU two-VM harness, physical-device signed transcripts, device identities, or identical APPLIED/DUPLICATE receipt hashes were supplied with this declaration or located in the verified GitHub release records at the time of finalization. An operator report is not independently reproduced test evidence.

A two-QEMU-guest run on one Windows computer, even if subsequently evidenced PASS, qualifies as **two isolated guest systems on one physical host**, not the two-independent-physical-device resilience condition in the original Gate 6 contract. Do not silently substitute one scope for the other.

## Acceptance ledger (append-only interpretation)

| Acceptance gate | Status | Supporting scope |
|---|---|---|
| G1 — 42 source identities / 8 views / 2,688 directed routes | **PASS** | Prior final-six CI acceptance. |
| G2 — reversible `{{d}}` four-port/three-coupler carrier | **PASS** | Prior final-six CI acceptance. |
| G3 — 214 B canonical ASTROPHAGE → 444 B OBF2 and Rust native/WASM parity | **PASS** | Prior final-six CI acceptance. |
| G4 — authenticated Ed25519 source and mTLS encrypted link | **PASS, scoped** | Authenticated durable relay CI; final RC1 local mTLS checks. |
| G5 — fsync-before-ACK journal / crash retry / duplicate detection | **PASS, scoped** | Integration CI and local crash/recovery tests; idempotent journal commit, **not** exactly-once external effects. |
| G6 — independent physical devices / disconnection / replay | **OPERATOR-REPORTED PASS; EVIDENCE PENDING** | The original external physical two-host criterion remains **UNVERIFIED**; the last documented plan uses two VMs on one laptop. |

### Certification decision

1. **Certify the implemented software release candidate as internally accepted for its *tested* identity, serialization, authentication, crash-recovery and local transport scope.**
2. **Accept and preserve the operator's Gate 6 PASS declaration as a historical attestation, not as an independently verified physical-device certification.**
3. **Finalize RC1 as a versioned, frozen-core software candidate. No changes to the frozen KET, `{{i}}`, `{{d}}`, OBS/dual-rail or OBF2 contracts.**
4. **Production public-network deployment remains HOLD.** A controlled single-writer LAN/VPN pilot may be undertaken only within the software's documented security and trust limits.
5. Original `FINAL_RELEASE-RC1.md`, `FINAL-SIX-COMPLETION-v2.md` and `TWO_DEVICE_SETUP.md` remain historical records. This addendum **does not retroactively overwrite their stated 5/6 evidence grade**.

## Primary source anchors

- Software integration CI, independently completed: https://github.com/DavidWise01/oasis/actions/runs/38590542771
- Original release candidacy and five-of-six ledger: `architecture/diatom-diamond/final-six/FINAL_RELEASE-RC1.md`
- Physical acceptance requirements: `architecture/diatom-diamond/final-six/TWO_DEVICE_SETUP.md`
- Single-Windows-host QEMU adaptation and its explicit limitation: `architecture/diatom-diamond/two-vm-laptop/README.md`
- Frozen OBS dual5 hash asserted and checked in prior CI: `47d4c89ac8155b9470852e0e23d2c059ad087eedc2b7949632a9431b5792fd4b`

## Minimal final evidence handoff

Keep private keys **off** GitHub. Publish only a sanitized `FINAL_RESULT.json` or receipt digest record stating the actual environment (physical A/B or QEMU guest A/B), sender/event ID, APPLIED and DUPLICATE acknowledgment statuses, exact same receipt hash, journal record count (one), restart/disconnect observed, signature/mTLS rejection behavior, test date, and the code commit tested.

Once reviewed and matched against the original acceptance conditions, append a **new evidence addendum** explicitly identifying which G6 scope passed; leave this report unchanged. Avoid another feature cycle.

## Post-signoff order

1. Pin the exact source commit and archive sanitized acceptance evidence and SHA-256 manifest.
2. If proof is VM-only, keep physical G6 open, and perform *one* real two-host run only if production resilience is required.
3. Pilot on a private LAN/VPN behind restricted firewall rules; retain one writer per journal and external backup.
4. Define rollback, key rotation, certificate expiration alert, journal integrity check, latency/error and duplicate/conflict monitoring.
5. Publish Confluence's verified observer receipts separately from the simulated UI. Do not relabel symbolic gates as physical laws or cryptographically verified facts.

**No third-party laboratory, security standard, regulatory compliance, independent auditor, or production-grade certification is claimed.**

`{{ KET :: RC1 FINALIZED :: FIELD PASS USER-ATTESTED :: PHYSICAL G6 EVIDENCE OPEN :: FROZEN CORE }}`
