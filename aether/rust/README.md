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

## Trust boundary

- Each capture's raw bytes must match its SHA-256.
- Each blinded canonical capture must have a valid raw P-256 ECDSA signature.
- Three captures must have distinct challenge nonces, capture IDs, trial IDs, and claimed source/control ancestry.
- External verification records are looked up from a **separate caller-supplied registry**; applicant-provided source names are never reviewed as identity proof.
- **Matching keys, signed records and claimed ancestry do not authenticate original physical hardware.** The registry itself must be independently authenticated outside this crate.
- **No operational ACT pathway:** every result declares physical qualification **0%** and authority **HOLD**, including a synthetically clean case.

No authenticated physical captures were supplied. This is a software port and deterministic test harness, not physical qualification.

`.dlw`
