# AETHER — Rust evidence verification

This Rust crate begins the migration of the `DavidWise01/oasis` AETHER evidence verification protocols. The implemented native bounds are **AETHER-190 — Blind External-Source Replay Audit**, **AETHER-191 — Physical Response & Alarm Documentary Screening**, **AETHER-192 — Documentary Freeze**, and **AETHER-193 — Original Evidence Intake**, and **AETHER-194 — Manufacturer/Calibration Credential Import**, and **AETHER-195 — Signed Challenge and Capture Receipt**, and **AETHER-196 — Signed Custody Export and Receiving Receipt**.

The previous JS verifier at [../190/verification.mjs](../190/verification.mjs), source labs, and GitHub Pages remain unchanged. The Rust implementation is not a drop-in browser replacement; it is the **native verification engine** and test target. HTML may consume future WebAssembly outputs after verification and integration.

## Run

```sh
cd aether/rust
cargo fmt --all
cargo clippy --all-targets --all-features
cargo test --all-targets
```

The GitHub workflow `.github/workflows/aether-rust.yml` runs these commands on Ubuntu using stable Rust.

## AETHER-191 alarm evidence\n\nThe native module [src/alarm.rs](src/alarm.rs) and [28 authored regression tests](tests/alarm_response.rs) cover signed capture bytes, reported device/reference measurements, response tolerance, traceability claims, alarm issuance/acknowledgement time ordering, and replay. It never verifies an actual physical alarm by itself. The [4D Pages dashboard](../191/) illustrates the failure cases; it does not execute Rust in the browser.\n\n## AETHER-193 original evidence intake\n\n[\`src/intake.rs\`](src/intake.rs) and [26 authored Rust regression tests](tests/original_intake.rs) implement SHA-256 integrity, P-256 signed capture records, challenge freshness, bounded intake size and separate declared custody-source ancestry. External issuer assertions remain unverified without out-of-band provenance. The [HTML laboratory](../193/) is a visualization, not a WASM build or hardware capture.\n\n## AETHER-194 external credential gates\n\nThe native [credential-import verifier](src/credentials.rs) and [28 authored test cases](tests/credential_import.rs) inspect manufacturer and calibration credential signatures against separately supplied pinned roots. Revocation, role, key usage and root ancestry are assessed; **a caller-supplied pin is not a verified manufacturer trust anchor**. The [neon visual lab](../194/) illustrates those rejections. Rust compilation and workflow results remain unverified.\n\n## AETHER-195 signed challenge and capture receipt\n\nThe native [challenge verifier](src/challenge.rs) and [28 authored regression tests](tests/challenge_receipt.rs) implement signed challenge, signed device capture receipt, payload SHA-256, challenge hash, expiry, bounded acquisition latency and replay checking against a supplied ledger. Only proposed ledger entries are returned after documentary acceptance; independent atomic ledger persistence is not implemented. The [neon HTML lab](../195/) illustrates these cases and does not execute Rust or authenticate physical hardware.\n\n## AETHER-196 custody export\n\nThe native [custody export verifier](src/custody_export.rs) and [32 authored integration tests](tests/custody_export.rs) verify the sender-signed manifest and receiver-signed acknowledgment, original byte SHA-256, predecessor custody digest, replay prevention and declared control separation. Signing a receiver receipt is not proof of physical possession. The [animated HTML laboratory](../196/) is a visualization and does not execute Rust. No original hardware was authenticated.\n\n## AETHER-197 signed calibration uncertainty\n\nThe native [calibration interval verifier](src/calibration.rs) and [22 authored Rust tests](tests/calibration_uncertainty.rs) check a signed calibration record and conservatively bound reported response uncertainty, rounded-up clock drift and decision-threshold crossing. A matching signed record is not out-of-band physical metrology traceability. The [4D neon visual laboratory](../197/) is illustrative, not a Rust runtime or original physical capture.\n\n## AETHER-199 physical response and alarm observer\n\nThe [Rust physical alarm gate](src/physical_alarm.rs) and [30 authored regression cases](tests/physical_alarm_observation.rs) evaluate two signed records with exact original capture and response digest linkage, distinct source/observer controls, bounded alarm and acknowledgment timing, response tolerance and replay checks. Synthetic claims and software passes never authenticate actual physical occurrence or authorize ACT. The [4D neon lab](../199/) is illustrative, not Rust-in-browser execution.\n\n## AETHER-200-RS Phase XV documentary freeze

The native [Phase XV freeze evaluator](src/phase_xv_freeze.rs) and [30 authored integration tests](tests/phase_xv_freeze.rs) check the [machine-readable AETHER-200 decision](../200/decision.json). The eight software protocol milestones (AETHER-193–200) are complete as historical documentary artifacts, with **0 authenticated original physical captures, 0 independently observed alarms, 0% physical qualification and operational ACT HOLD**.

The [animated 4D Pages laboratory](../200/) displays the JSON and illustrates the freeze. It does not execute the Rust crate. Runtime compilation and GitHub Actions pass status remain unverified. A Git branch is not inherently immutable and the freeze is a documented historical decision, not external physical evidence.

## AETHER-201-RS local durable replay ledger

The [native ledger](src/durable_ledger.rs) and [18 authored integration tests](tests/durable_ledger.rs) add a local JSON Lines SHA-256 chain, exclusive lock-file writer arbitration, append-and-fsync, directory sync, recovery readback, stale-head rejection, and event/nonce/capture/review/payload replay screening. The [4D neon Pages laboratory](../201/) visualizes failure states but does not persist data or execute Rust.

**Security limits:** An orphan lock fails closed; no authenticated process-liveness fencing yet. A torn tail is rejected, not automatically repaired. The local file can be rolled back or deleted without an independent trusted checkpoint. Fsync is not external witness custody. Physical qualification stays 0%, operational ACT stays HOLD. Compilation and CI test outcomes remain unverified.

## AETHER-202-RS Linux process identity

The [Linux process-liveness guard](src/process_liveness.rs) and [20 authored Rust integration tests](tests/process_liveness.rs) add OS-observed PID, `/proc` process-start ticks and kernel boot identity to the lock acquired by [AETHER-201's durable replay ledger](src/durable_ledger.rs). The guard writes fsynced mode-0600 metadata under exclusive create and refuses to release a replaced or ownership-mismatched lock. It **never automatically reclaims a lock**, even if the owner has exited.

[The animated 4D Pages laboratory](../202/) illustrates state transitions but does not access Linux process information or run Rust. Local process identity is not independent external custody. The process-liveness implementation is Linux-only; no pidfd/distributed fencing or complete protection against hostile path mutation is claimed. Physical qualification stays 0% and ACT HOLD. Compilation and CI execution require separate verification.

## AETHER-203-RS signed recovery checkpoint

The [native checkpoint verifier](src/recovery_checkpoint.rs) and [25 authored integration tests](tests/recovery_checkpoint.rs) compare a locally validated ledger history to an independently pinned, ECDSA P-256 signed holder checkpoint. The exact checkpoint digest and holder public-key fingerprint must be provisioned outside the submitted evidence, or the output has no independent evidentiary authority. Truncated, deleted, forked or tampered ledger histories are rejected, as are replayed checkpoint identifiers and shared source-holder ancestry.

The [4D neon laboratory](../203/) illustrates these cases without running Rust. The [ledger append integration](src/durable_ledger.rs) enforces expected-head and count compare-and-append, but checkpoint validation is performed **before** taking the OS lock; an atomic re-verification under that same lock is deferred to AETHER-204. No independent holder has yet been authenticated, no physical qualification is conferred, and ACT always remains HOLD. Cargo and Actions verification remain unconfirmed.

## AETHER-204-RS atomic checkpoint admission under one process-owned lock

The [signed recovery gate](src/recovery_checkpoint.rs) and [durable ledger](src/durable_ledger.rs) now hold **one verified OS-owned Linux lock** through complete checkpoint-history revalidation, expected-head admission, fsynced append, full JSONL readback, and committed-record verification. The [lock guard](src/process_liveness.rs) rechecks lock-file owner identity, inode and kernel-observed process identity before and after the critical operation.

[20 authored Rust regression tests](tests/atomic_checkpoint.rs) cover lock contention, stale head, intervening writes, torn/corrupted/truncated history, replay, forged checkpoint evidence, and lock-file tampering. The [4D neon laboratory](../204/) is a browser visualization; it does not run Rust or authenticate external custody.

This strengthens local atomicity but does not implement remote checkpoint storage or an authenticated independent holder. It is not a defense against every hostile directory race or distributed filesystem operation, and cannot authorize lock reclamation or physical ACT. Physical qualification remains **0%**; operational authority **HOLD**. Cargo, CI and Pages live execution remain unverified.

## AETHER-205-RS independently pinned custody issuer and holder

The native [external custody gate](src/external_custody.rs) and [33 authored regression cases](tests/external_custody.rs) verify separate ECDSA P-256 issuer and holder signatures on the same admission record, independently provisioned public-key fingerprints, non-overlapping declared source/issuer/holder ancestry, revocation and nonce replay. A holder-key rotation requires a separately pinned and signed authority approval with a distinct root and matching policy epoch.

The [animated 4D neon laboratory](../205/) illustrates six fail-closed custody cases; it does not execute native Rust or connect to a physical holder. **Signer root labels and caller authentication flags alone do not establish real-world independence.** There has been no authenticated external custody holder or physical source, and the gate is not yet wired to the same critical section as AETHER-204's durable append. Physical qualification remains **0%**, ACT **HOLD**. Cargo, CI, and live Pages validation remain separate checks.

## AETHER-206-RS custody-bound atomic journal transition

The native [custody-commit module](src/custody_commit.rs) and [24 authored regression tests](tests/custody_commit.rs) bind the AETHER-205 issuer and holder signatures to a separately signed canonical transition intent, which includes the exact AETHER-203 checkpoint digest, custody-admission digest, expected journal head, next sequence, event digest and each event identifier. The [AETHER-204 single-lock append](src/durable_ledger.rs) performs full hash-chain readback and fsync while the same Linux process-owned lock is held.

The [4D neon lab](../206/) visualizes synthetic rejection paths, but cannot run Rust or prove remote custody. Out-of-band physical issuer/holder authentication and independently persisted revocation/replay authority are **not provided**. Local atomicity is not an atomic remote custody transaction. The Rust tests and Pages deployment still require independent runtime verification. Physical qualification stays **0%** and ACT **HOLD**.

## AETHER-207-RS persistent replay and revocation registry

The [native authorization registry](src/authorization_registry.rs) and [41 authored Rust tests](tests/authorization_registry.rs) persist the journal head/count, consumed custody admission and signed transition IDs/nonces/digests, revocation epoch, and monotonic revoked-key set. The [AETHER-206 custody-bound append](src/custody_commit.rs) is now callable under a registry-owned, OS-verified Linux process lock; both ledger append and registry publication occur under the same lock. A signed P-256 revocation amendment separately pins revocation authority, proof ancestry and a strictly increasing epoch. The [4D neon Pages laboratory](../207/) illustrates the failure modes without executing Rust.

**Important:** Ledger fsync followed by registry rename is not one atomic two-file transaction. Any interrupted write may leave divergence; the next call refuses admission until independently approved recovery. An attacker able to roll back *both* files may evade this local comparison without an externally retained checkpoint. Root enrollment and external identity authentication are not independently established. No actual original physical capture or external custody was observed; physical qualification **0%**, ACT **HOLD**. Cargo compilation, tests, Actions and live Pages deployment remain unverified.

## AETHER-208-RS — Phase XVI documented freeze

The [Phase XVI Rust freeze evaluator](src/phase_xvi_freeze.rs) and [39 authored regression tests](tests/phase_xvi_freeze.rs) inspect the [AETHER-208 decision record](../208/decision.json). Phase XVI's eight documentary software milestones AETHER-201–208 are recorded as closed; original physical captures, independently authenticated external roots, external remote checkpoints, and physically witnessed alarms remain **0**. Physical qualification is **0%**, operational ACT **HOLD**.

The [4D neon laboratory](../208/) illustrates the documentary freeze and inspects the JSON in-browser, but does not run native Rust or independently authenticate source custody. Neither Cargo compilation, tests, GitHub Actions result nor actual Pages deployment is certified by this freeze. The ledger and registry are **two files without joint crash atomicity**, and simultaneous rollback remains undetectable without a separately held trusted checkpoint. A Git commit is a historical documentary anchor, not proof of an immutable branch or remote physical custody. Any later physical-evidence review must be a new bound with explicit independent provenance.

## Trust boundary

- Each capture's raw bytes must match its SHA-256.
- Each blinded canonical capture must have a valid raw P-256 ECDSA signature.
- Three captures must have distinct challenge nonces, capture IDs, trial IDs, and claimed source/control ancestry.
- External verification records are looked up from a **separate caller-supplied registry**; applicant-provided source names are never reviewed as identity proof.
- **Matching keys, signed records and claimed ancestry do not authenticate original physical hardware.** The registry itself must be independently authenticated outside this crate.
- **No operational ACT pathway:** every result declares physical qualification **0%** and authority **HOLD**, including a synthetically clean case.

No authenticated physical captures were supplied. This is a software port and deterministic test harness, not physical qualification.

`.dlw`
