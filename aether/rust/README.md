# AETHER — Rust evidence verification

This Rust crate begins the migration of the `DavidWise01/oasis` AETHER evidence verification protocols. The implemented native bounds are **AETHER-190 — Blind External-Source Replay Audit**, **AETHER-191 — Physical Response & Alarm Documentary Screening**, **AETHER-192 — Documentary Freeze**, and **AETHER-193 — Original Evidence Intake**, and **AETHER-194 — Manufacturer/Calibration Credential Import**, and **AETHER-195 — Signed Challenge and Capture Receipt**.

The previous JS verifier at [../190/verification.mjs](../190/verification.mjs), source labs, and GitHub Pages remain unchanged. The Rust implementation is not a drop-in browser replacement; it is the **native verification engine** and test target. HTML may consume future WebAssembly outputs after verification and integration.

## Run

```sh
cd aether/rust
cargo fmt --all
cargo clippy --all-targets --all-features
cargo test --all-targets
```

The GitHub workflow `.github/workflows/aether-rust.yml` runs these commands on Ubuntu using stable Rust.

## AETHER-191 alarm evidence\n\nThe native module [src/alarm.rs](src/alarm.rs) and [28 authored regression tests](tests/alarm_response.rs) cover signed capture bytes, reported device/reference measurements, response tolerance, traceability claims, alarm issuance/acknowledgement time ordering, and replay. It never verifies an actual physical alarm by itself. The [4D Pages dashboard](../191/) illustrates the failure cases; it does not execute Rust in the browser.\n\n## AETHER-193 original evidence intake\n\n[\`src/intake.rs\`](src/intake.rs) and [26 authored Rust regression tests](tests/original_intake.rs) implement SHA-256 integrity, P-256 signed capture records, challenge freshness, bounded intake size and separate declared custody-source ancestry. External issuer assertions remain unverified without out-of-band provenance. The [HTML laboratory](../193/) is a visualization, not a WASM build or hardware capture.\n\n## AETHER-194 external credential gates\n\nThe native [credential-import verifier](src/credentials.rs) and [28 authored test cases](tests/credential_import.rs) inspect manufacturer and calibration credential signatures against separately supplied pinned roots. Revocation, role, key usage and root ancestry are assessed; **a caller-supplied pin is not a verified manufacturer trust anchor**. The [neon visual lab](../194/) illustrates those rejections. Rust compilation and workflow results remain unverified.\n\n## AETHER-195 signed challenge and capture receipt\n\nThe native [challenge verifier](src/challenge.rs) and [28 authored regression tests](tests/challenge_receipt.rs) implement signed challenge, signed device capture receipt, payload SHA-256, challenge hash, expiry, bounded acquisition latency and replay checking against a supplied ledger. Only proposed ledger entries are returned after documentary acceptance; independent atomic ledger persistence is not implemented. The [neon HTML lab](../195/) illustrates these cases and does not execute Rust or authenticate physical hardware.\n\n## Trust boundary

- Each capture's raw bytes must match its SHA-256.
- Each blinded canonical capture must have a valid raw P-256 ECDSA signature.
- Three captures must have distinct challenge nonces, capture IDs, trial IDs, and claimed source/control ancestry.
- External verification records are looked up from a **separate caller-supplied registry**; applicant-provided source names are never reviewed as identity proof.
- **Matching keys, signed records and claimed ancestry do not authenticate original physical hardware.** The registry itself must be independently authenticated outside this crate.
- **No operational ACT pathway:** every result declares physical qualification **0%** and authority **HOLD**, including a synthetically clean case.

No authenticated physical captures were supplied. This is a software port and deterministic test harness, not physical qualification.

`.dlw`
