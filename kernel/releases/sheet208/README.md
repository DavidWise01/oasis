# SHEET 208 — Internal Signed Ownership Audit (INCOMPLETE)

Local gate: **16/16 test assertions pass**, including one explicit **counterexample** showing that a still-valid epoch-1 signed ownership token can append to the WAL after epoch 2 has been issued. Mandatory stale-owner rejection is therefore **NOT PASSED**.

The S176-derived `transaction208.js` checks signed ownership claims inside `invoke`, including nonce, expiration and WAL path. Direct invocation without a proof fails. However the writer does not consult a live, serializable epoch authority during the protected append; a signed token alone is not revocation.

Tested source and gate: `SHEET208-internal-fence-audit.zip` (44,512 bytes) SHA-256 `205f943fd45c1fa563fa907fe04e357ecc97b0aa80b8c4cdab2bf6fce323af5a` distributed in conversation. This GitHub commit records the audit only; executable files are in ZIP.

Next acceptance target: synchronize epoch issuance and WAL append under one enforceable storage boundary; reject the stale epoch counterexample; isolate direct legacy S176 writes and test SIGKILL and concurrent writers.
