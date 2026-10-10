# SHEET 169 — Authenticated Witness Transport

**Prototype gate:** 24/24 PASS (`node gate169.js`). Inherits `quorum167.js` and `runtime168.js` and adds TLS 1.3 mutual-certificate witness RPCs. Three isolated local processes exercise a 2-of-3 Ed25519 decision certificate, single witness loss, forked generation refusal, persisted hysteresis samples, signed checkpoint, and quarantine after torn persistence.

**Executable release:** `SHEET169-authenticated-witness-quorum.zip` available as a conversation artifact. SHA-256 `5affb52e8a874da8015081d3350ac8c3d8992f32eb124384ae14a9ad16b67ac2` (8392 bytes). This GitHub commit is a release record only; executable implementation is in the ZIP.

**Strict verification boundary:** All witness processes run on one host and use an ephemeral test CA. This is not cross-host or partition-tested consensus, there is no independently protected anti-rollback floor or identity-scoped ACL, and the SHEET 166 live mTLS/Merkle recovery path has not been integrated or rerun. Full historical regression suite not executed.

Next SHEET 170: deploy distinct hosts, separate durable floors, scope certificate identities, integrate the source/target recovery cursor with quorum authorization and run partition fault tests.
