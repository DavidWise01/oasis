# AETHER — Rust evidence verification

This Rust crate begins the migration of the `DavidWise01/oasis` AETHER evidence verification protocols. The first implemented bound is **AETHER-190 — Blind External-Source Replay Audit**.

The previous JS verifier at [../190/verification.mjs](../190/verification.mjs), source labs, and GitHub Pages remain unchanged. The Rust implementation is not a drop-in browser replacement; it is the **native verification engine** and test target. HTML may consume future WebAssembly outputs after verification and integration.

## Run

```sh
cd aether/rust
cargo fmt --all -- --check
cargo clippy --all-targets --all-features -- -D warnings
cargo test --all-targets
```

The GitHub workflow `.github/workflows/aether-rust.yml` runs these commands on Ubuntu using stable Rust.

## Trust boundary

- Each capture's raw bytes must match its SHA-256.
- Each blinded canonical capture must have a valid raw P-256 ECDSA signature.
- Three captures must have distinct challenge nonces, capture IDs, trial IDs, and claimed source/control ancestry.
- External verification records are looked up from a **separate caller-supplied registry**; applicant-provided source names are never reviewed as identity proof.
- **Matching keys, signed records and claimed ancestry do not authenticate original physical hardware.** The registry itself must be independently authenticated outside this crate.
- **No operational ACT pathway:** every result declares physical qualification **0%** and authority **HOLD**, including a synthetically clean case.

No authenticated physical captures were supplied. This is a software port and deterministic test harness, not physical qualification.

`.dlw`
