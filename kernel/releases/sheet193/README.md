# SHEET 193 — Authenticated Floor Authority and SIGKILL Gate

Local gate: **18/18 PASS**. Real HTTPS service on separate loopback process with test CA and mutual TLS, an independently generated Ed25519 signing key, and SQLite monotonic signed floor. Replayed/forked generation, forged signature and missing client certificate rejected. A separate worker is killed with real SIGKILL after persisting BOUND_PENDING_FLOOR, and an authority outage cannot mark the state verified.

**Tested executable artifact:** `SHEET193-mtls-sigkill-floor-gate.zip`, 58603 bytes, SHA-256 `571f605d625176217335c9e19c147d5844fd6f9baab64f8af1b0fbc3116bab79`. Includes `authority193.py`, `gate193.py`, `worker193.py`, README and inherited S192 package. The ZIP is the tested authoritative source tree. GitHub's worker alone is not the complete gate.

**Boundary:** Single physical host, ephemeral CA; worker state is an S192-style fixture rather than direct call through S190–S192 repair. The authority does not verify remote target receipts on each request. No protected remote authority, partition testing, hardware rollback defense, or physical power-loss testing; no inherited gate rerun. No production distributed-consensus claim.

**Next S194:** require a target-signed receipt plus authorized repair certificate on the mTLS endpoint itself, and verify restart/persistence under network failures.
