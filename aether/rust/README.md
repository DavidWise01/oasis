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

## AETHER-209-RS independently pinned remote anchor observation

The [external recovery-anchor verifier](src/remote_anchor.rs) and [25 authored regression cases](tests/remote_anchor.rs) compare the locally verified JSONL journal and authorization registry to a separately pinned, ECDSA P-256 signed checkpoint. An anchor contains the ledger sequence/head hash, the complete registry snapshot SHA-256, revocation epoch, holder/source/issuer ancestry and predecessor digest. It detects a locally consistent journal and registry that have both been truncated below an independently retained checkpoint.

The [4D neon browser laboratory](../209/) is a synthetic display and never executes Rust or contacts an external custodian. The new Rust gate is explicitly observation-only: `may_append = false`, `may_recover = false`, physical ACT false. No authentic external remote receipt or physically witnessed original evidence was supplied. The externally supplied trust pin and authentication booleans do not establish independence on their own. Cargo, tests, CI and Pages deployment remain unverified. Phase XVI's [documentary freeze](../208/decision.json) remains unchanged.

## AETHER-210-RS durable local receipt custody

The [receipt custody Rust module](src/receipt_custody.rs) and [25 authored integration tests](tests/receipt_custody.rs) add an append-only local JSONL receipt chain using ordered SHA-256 links, exclusive Linux process-owner lock, expected-head/sequence checks, replay protection, fsync and complete readback. Every copied receipt is tied to an AETHER-209 signed anchor, separately supplied key pins and a claimed holder/source locator. The [animated 4D neon Pages laboratory](../210/) illustrates failure decisions only; it does not execute Rust.

**External evidence boundary:** a local copy of a signed remote receipt is not independently retained remote custody. The submitted `remote_receipt_sha256` is the anchor's claimed content digest, not independently fetched remote bytes. Local receipt storage is separate from the ledger's lock, and neither joint rollback nor distributed atomicity is solved. Zero remote holders or original physical captures are independently authenticated. Both `may_recover` and physical ACT remain disabled. Compilation, tests, Actions and live Pages deployment remain unverified.

## AETHER-211-RS monotonic signed receipt refresh

The [forward-extension Rust verifier](src/monotonic_receipt.rs) and [25 authored regression tests](tests/monotonic_receipt.rs) require an exact previous signed-anchor SHA-256 digest, strictly increasing ledger sequence and changed head, nondecreasing registry epoch, and unchanged source/issuer ancestry. Holder identity/key changes require a separately pinned P-256 signed rotation approval from a distinct declared authority with an authorization ID and nonce.

The [receipt custody module](src/receipt_custody.rs) adds `ingest_monotonic`, which runs these checks **under the same local Linux receipt-store lock** used for replay screening, journal append, fsync and readback. The original `ingest` API remains for backward compatibility; callers requiring monotonic ancestry must explicitly select the new one.

[Neon 4D Pages laboratory](../211/) illustrates the failure outcomes but does not run Rust. Independent physical custody, remote availability, persistent rotation-policy replay state and cross-store atomicity remain unverified. Timestamps are not authorization. Authenticated remote receipts **0**; physical qualification **0%**; recovery and ACT **HOLD**. Compilation, regression execution, Actions and Pages deployment remain unverified.

## AETHER-212-RS read-only crash incident reconciliation

The [Rust incident observer](src/crash_incident.rs) and [21 authored regression tests](tests/crash_incident.rs) compare the local evidence journal, authorization registry and receipt-custody journal without changing any of them. They record byte-level SHA-256 snapshots and validated head/count summaries, detect torn or corrupt histories, missing stores, pending registry updates, outstanding process locks and receipt claims beyond the available journal/registry epoch. A second filesystem read detects some intervening writes but cannot make a three-file snapshot atomic.

The [4D neon Pages lab](../212/) illustrates six synthetic forensic decisions without running Rust. The module cannot repair a journal, reconcile persisted records, seize a lock, authenticate a remote holder or grant physical ACT. Local consistency does not prove original remote custody, and jointly rolled-back local files may still appear internally coherent. Independently authenticated remote receipts: **0**. Physical qualification **0%**, ACT **HOLD**. Cargo, tests, CI and live Pages verification remain pending.

## AETHER-213-RS signed custody-ancestry incident screening

The [Rust witness-ancestry evaluator](src/custody_ancestry.rs) and [30 authored regression cases](tests/custody_ancestry.rs) bind exactly three P-256 signed observation envelopes to the SHA-256 digest of the [AETHER-212 incident](src/crash_incident.rs). Each envelope records its source corpus, declared controlling root/operator/administrator, host, signature key fingerprint, evidence hash and receipt reference. Declared source/witness controller overlap, mirror ancestry, reused receipts, shared witness administrators/operators/hosts and invalid pins or signatures fail closed.

The [AETHER-213 neon 4D lab](../213/) is an illustrative HTML display, not a cryptographic execution environment. The documentary verdict does not certify independent remote control, original physical capture or independently retained external witnesses. GitHub and 0root.ai copies of one corpus are not two independent sources. Claimed enrollment and receipt-retention flags are inputs, not proof of real-world independence. Independently authenticated physical witnesses remain **0**; qualification **0%**; recovery and ACT **HOLD**. Cargo compilation, test execution, Actions and live Pages checks remain unverified.

## AETHER-214-RS signed cross-host equivocation screening

The [Rust cross-host verifier](src/cross_host_equivocation.rs) and [30 authored adversarial tests](tests/cross_host_equivocation.rs) preserve conflicting signed claims about the same ledger sequence, head, predecessor, registry snapshot or epoch; detect adjacent-sequence forks and revocation epoch rewind; and screen claimed source/witness root, operator, administrator, host and key ancestry. Signing keys are verified against individually pinned P-256 public keys, but cryptographic validity cannot establish independently controlled remote custody.

The [4D neon Pages lab](../214/) illustrates six synthetic cases without contacting remote hosts or running Rust. The gate never chooses a winner by quorum, timestamp or signature count. Conflict receipts remain documentary evidence, and the result has `may_choose_history=false`, `may_recover=false`, physical qualification **0%** and ACT **HOLD**. Three separately hosted copies under one controller are not three independent witnesses. Rust compilation, regression execution, CI and deployed Pages runtime remain unverified.

## AETHER-215-RS integrated adversarial remote-custody qualification

The [Rust qualification gate](src/adversarial_qualification.rs) and [24 authored regression cases](tests/adversarial_qualification.rs) bind exact SHA-256 digests for the read-only AETHER-212 incident, signed AETHER-213 custody-witness envelope, and AETHER-214 cross-host receipt ensemble. They independently recheck signed evidence, reject conflicting predecessor/ledger/registry histories, and compare source ancestry, witness identity, receipt references, signing keys, root/operator/admin and host controls across both witness protocols.

The [neon 4D Pages lab](../215/) illustrates six synthetic fault categories; it neither executes Rust nor communicates with remote custodians. A positive documentary finding cannot establish real independent control: even fully signed, synthetically consistent claims **cannot authorize recovery, repair, lock reclamation, contested history selection or physical ACT**. No physically authenticated original evidence or remote holder has been observed, and the external enrollment/retention fields are caller-supplied assertions. Physical qualification is **0%**; ACT **HOLD**. Cargo, tests, GitHub Actions success and live Pages deployment remain unverified.

## AETHER-216-RS — Phase XVII final documentary freeze

The [Phase XVII Rust freeze evaluator](src/phase_xvii_freeze.rs) and [45 authored regression cases](tests/phase_xvii_freeze.rs) check the [machine-readable AETHER-216 decision](../216/decision.json). All eight AETHER-209–216 software authoring milestones are recorded as closed. This is **not** native execution certification, independent remote custody, physically authenticated original evidence or operational authority.

The [animated 4D neon Pages laboratory](../216/) inspects the final JSON using browser logic but does not run native Rust or independently verify external witnesses. Authenticated original hardware captures **0**, authenticated independent physical witnesses **0**, independently retained external checkpoints **0**, physical qualification **0%**, recovery and ACT **HOLD**.

Historical problems remain recorded: journal, registry and receipt store updates are not one crash-atomic transaction; local copies do not prove externally retained receipts; three valid signatures can share one controller; unresolved signed host forks cannot be voted away; no independent acquisition or alarm has been physically observed. Cargo compilation, regression execution, GitHub Actions and live Pages runtime remain unverified. The Phase XVI freeze is preserved unchanged.

## Trust boundary

- Each capture's raw bytes must match its SHA-256.
- Each blinded canonical capture must have a valid raw P-256 ECDSA signature.
- Three captures must have distinct challenge nonces, capture IDs, trial IDs, and claimed source/control ancestry.
- External verification records are looked up from a **separate caller-supplied registry**; applicant-provided source names are never reviewed as identity proof.
- **Matching keys, signed records and claimed ancestry do not authenticate original physical hardware.** The registry itself must be independently authenticated outside this crate.
- **No operational ACT pathway:** every result declares physical qualification **0%** and authority **HOLD**, including a synthetically clean case.

No authenticated physical captures were supplied. This is a software port and deterministic test harness, not physical qualification.

`.dlw`
