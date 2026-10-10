# SHEET 218 — Authenticated Durable Input Provenance

**Real executed tests:** 15/15 new provenance checks, 27/27 live mTLS recovery integration checks, 9/9 S217 execution regression, 13/13 S216 semantic regression. **64/64 focused checks PASS.**

New immutable SQLite ledger indexes input by resource and transaction nonce; Ed25519 issuer signs operation, input, identifiers and input digest. The S218 mTLS target refuses request-supplied execution and retrieves its input only from signed durable ledger before invoking the separate Node S175 evaluator and signing its target receipt.

**Exact packaged source with all runnable gates:** SHEET218-authenticated-input-provenance.zip, 63 files, 87,601 bytes. SHA-256: `969dcd554b66df71c3001498098fece91907efcca22005e14ccf218d0b9e17b2`. Run `python gate218.py && python gate218_integration.py && python gate217.py && python gate216.py` in extracted root.

**Scope and security limits:** same-host test PKI and issuer keys; no production-independent source attestation. Registration trust is anchored on a local issuer key, not a proven external business origin. Ledger lookup and target SQLite commit not one transaction; WAL and SQLite not atomic. Historical unprotected target endpoints remain in predecessor source and must be removed from production routing. No cross-host, power-loss or dedicated-UID regression in S218.

Next S219: input-ledger writer-side binding and durable snapshot/fencing.
