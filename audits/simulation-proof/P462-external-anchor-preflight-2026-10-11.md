# ROOT0 P4.62 — Remote anchor preflight and fail-closed receipt verification

2026-10-11. Local Node 22.16.0 regression: **19/19 assertions PASS**, 24.008ms including deliberate 20ms timeout.

New `p462_gate.mjs` validates nonce/deployment-bound Ed25519-signed witness receipts and detects primary history below anchored epoch (rollback), equal-epoch conflicting heads (fork), and primary ahead of anchor (not yet witnessed). A promised external endpoint's preflight requires HTTPS, nonloopback address, pinned public-key digest, and an operator-supplied independent-custody attestation. The local callback adapter rejects malformed/tampered/forged replies, offline and timeout failures. Test exercises 19 cases including plaintext refusal, loopback rejection, missing pin, and missing custody attestation.

**Critical limitation:** No real second host is connected; responses are mocked by a local test callback, preflight cannot validate independent administrators or external power/rollback protection, and the module doesn't itself perform HTTPS. These are security prerequisites rather than proof of multi-host operation. Consequently **14/20 = 70%** prototype roadmap, unchanged.

Complete executable source, test, README and results packaged in downloadable `p462_bundle.zip`, SHA-256 `b7779c9de3462bac7e65ba9e484ef45188645cdf64ff8d688e7a31133a09841e`. GitHub audit committed; complete executable module remains in ZIP.

Next P4.63: remote HTTPS adapter integration with TLS hostname/certificate verification, per-request secure nonce, and authenticated external trust-domain evidence.