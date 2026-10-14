# OASIS/KET — Six final production acceptance gates

Date: 2026-10-14. GitHub Actions run: https://github.com/DavidWise01/oasis/actions/runs/38521457161

**Harness execution: PASS (all six gates executed successfully)**  
**Production readiness: HOLD (not all requirements passed)**

No changes to frozen KET, `{{i}}`, `{{d}}`, OBS dual-floor or OBF2 v2.1.

| Gate | Objective | Result | Verified finding |
|---|---|---|---|
| **1** | **`{{i}}` coordinate identity** | **PASS** | 42 unique coordinates, eight views, 2,688 directed transitions. Duplicate displayed `0` tokens remain distinct, six-stage graded `{{i}} < {{so}} << {{more}} <<< {{Pp}} <<<< {{i}} <<<<< {{CcC}}` retains both identity positions. |
| **2** | `{{d}}` four-port/three-coupler diamond | **PASS** | All 42 canonical identities round-trip across every source/target view, no lost lane/slot coordinates or reordering. |
| **3** | ASTROPHAGE / OBF2 transport and Rust native/WASM parity | **PASS** | Canonical 214-byte message encodes to a 444-byte OBF2 frame; native Rust TCP and Rust WASM (Node-hosted TCP) independently return identical frames. Corrupt CRC rejected. |
| **4** | Trust: sender authentication and provenance | **GAP** | Demonstrably accepts a forged, internally consistent OBF2 message without sender credentials. Valid CRC and two matching rails **do not authenticate origin or prove semantic truth**. Must add authentication above frozen OBF2. |
| **5** | Reconnection, restart and durable recovery | **PARTIAL** | Server process restarted; message could be resent and recovered identically. No persistent ACK state, durable commit log, duplication suppression or exactly-once delivery was demonstrated. |
| **6** | Bounded traffic and full end-to-end stability | **PARTIAL** | 12 concurrent loopback connections recovered the exact field; an oversized frame was rejected. No two-machine WAN test, controlled loss/jitter, peer authentication, or robust long-term load assessment. |

### Decision

**HOLD production freeze.** Identity, reversible serialization and single-host network transport are working. Do not claim all six PASS because gates 4, 5, and 6 are not fully satisfied.

To finish with minimal work and without another large test matrix:

1. Integrate cryptographic source authentication (e.g., Ed25519 signature or authenticated TLS with recorded sender IDs), plus versioned, auditable provenance. Authentication confirms identity/integrity, not whether a scientific claim is true.
2. Implement persistent receive/ACK journal and replay policy with stable event IDs. State the supported semantics (at-least-once, idempotent processing, or exactly-once effect) explicitly.
3. Run **one** final integrated test on two real devices to verify the authenticated message, abrupt restart and resumable ACK, simultaneous connections, and realistic packet loss/delay.

These are genuine implementation gaps, not a request for thousands of redundant benchmarks.

### Reproduce

`architecture/diatom-diamond/final-six/final-six.mjs` is the exact deterministic six-gate runner. GitHub Actions workflow `.github/workflows/oasis-final-six.yml` compiles one existing Rust codec for native and WebAssembly, verifies the frozen-floor SHA-256, runs exactly six gates and archives machine-readable `final-six-results.json`.

The script reports `suiteExecution: PASS`, `productionDecision: HOLD`. CI execution success **is not** the same as production acceptance.

**Scope:** These are classical software correctness/transport checks, not physical entanglement experiments or claims of zero network propagation time.
