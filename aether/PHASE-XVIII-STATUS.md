# AETHER Phase XVIII — Executable Rust Qualification & Independent Evidence Acquisition

**AETHER-217-RS RUST EXECUTABLE QUALIFICATION GATE COMMITTED. Phase XVIII documentary software progress 1/8 = 12.5%. Native compilation and GitHub Actions result: NOT VERIFIED. Independently authenticated original physical captures: 0. Physical qualification: 0%. Operational ACT: HOLD.**

The [AETHER-216 Phase XVII freeze](216/decision.json) remains historically intact, with eight authored Phase XVII documentary milestones closed and all physical authority withheld. Phase XVIII separates verified *execution* from source-only acceptance and independently anchored external acquisition from locally copied evidence.

| Turn | Software milestone | Status | Phase progress |
|---|---|---|---:|
| 1 | 217 Executable qualification and reproducible Rust CI evidence | **COMMITTED — execution pending verification** | **12.5%** |
| 2 | 218 Native compile-failure triage and fail-closed regression repair | Planned | 12.5% |
| 3 | 219 Deterministic test fixture and reproducible artifact manifest | Planned | 12.5% |
| 4 | 220 Browser-to-native parity and controlled artifact validation | Planned | 12.5% |
| 5 | 221 External custody enrollment evidence interface | Planned | 12.5% |
| 6 | 222 Out-of-band challenge and origin verification | Planned | 12.5% |
| 7 | 223 Adversarial qualification and independent physical-evidence review | Planned | 12.5% |
| 8 | 224 Phase XVIII documentary software decision and freeze | Planned | 12.5% |

## AETHER-217-RS — Executable Rust qualification

- [Native Rust CLI](rust/src/bin/aether217_qualification.rs) embeds the historical [AETHER-216 freeze](216/decision.json), deserializes it, runs the Phase XVII freeze evaluator and emits a machine-readable JSON report. If freeze consistency or the physical ACT HOLD invariants fail, the executable exits unsuccessfully.
- [Four authored integration tests](rust/tests/executable_qualification.rs) execute the CLI when run by Cargo, checking its documentary verdict, zero external evidence, prohibited recovery/ACT and honest separation between binary execution and full test-suite evidence.
- [GitHub Actions workflow](../.github/workflows/aether217-rust-qualification.yml) targets Ubuntu 24.04 with the stable Rust toolchain. On push or manual dispatch it records Git commit/toolchain versions, attempts `cargo check --all-targets`, runs `cargo test --all-targets -- --nocapture`, executes the qualification binary, and uploads the JSON report with source/toolchain metadata. **Committing a workflow does not certify that a run started or passed.**
- [Neon 4D HTML laboratory](217/) retains the animated 16-vertex/32-edge tesseract and inspects the static AETHER-217 protocol. It does not execute Rust or report real CI success. [Protocol](217/protocol.json) declares **Phase XVIII 1/8 = 12.5%**.
- **Trust boundary:** native compilation, test execution, and live Pages deployment are not verified in this environment. Even passing CI does not provide original physical capture, independent remote custody, physical qualification or operational ACT; all remain at **0% / HOLD**. Existing frozen Phase XVII assertions remain unchanged.
- **Next AETHER-218-RS:** read actual Rust CI failures, resolve compilation or test defects on current non-frozen sources, and rerun until the qualification gate is verifiably executable without weakening any documented safety invariant. `.dlw`

**Phase XVIII: 12.5% documentary milestone progress. Physical 0%. ACT HOLD.**
