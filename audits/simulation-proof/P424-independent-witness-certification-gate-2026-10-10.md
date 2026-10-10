# ROOT0 P4.24 — documentary independent-host certification gate (2026-10-10)

Locally verified on Node.js v22.16.0: **18/18 assertions PASS**, elapsed ~5.62 ms (corrected run). P4.24 `evaluateCertification` requires distinct self-asserted host/admin/key custody values, a signed Ed25519 deployment record, checkpoint digest/epoch, and four PASS evidence hashes (controller rollback, outage, forgery, restart). It rejects absent/duplicated/failed tests, corrupt signatures, shared host/admin/key domain, and explicitly simulated tests when production mode requested. P4.23 same-host deployment fails the gate.

**Certification status for actual ROOT0 deployment: NOT CERTIFIED.** The test uses a locally generated synthetic signed attestation describing imaginary distinct hosts. Matching string labels and hashes does NOT prove host independence, administration or evidence authenticity, and an attesting administrator could lie. The gate enforces documentary policy, not independent external fact verification. No second host, hardware monotonic witness, TPM attestation, cross-host outage or recovery run in this turn. The `certified` return flag means 'passes documentary checks', **not actual security certification**.

Source and regression committed in `docs/reality-tensor/dyson-inversions/`. Complete executable ZIP SHA-256: `1a4938b1f7b7d72bee63fda9978180a72c10af43cfbbd570952f95af43f986ee`.

Next P4.25: independent verifier challenge-response and cryptographic linkage to actual remote server attestations and test artifacts.