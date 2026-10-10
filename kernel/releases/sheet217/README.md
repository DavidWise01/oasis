# SHEET 217 — Independent Target Result Reproduction

**Verified local gates:** 9/9 new result-execution checks + 13/13 S216 semantic regression + 26/26 live mTLS S215 recovery checks = **48/48 PASS**. Target now requires op and input for `/commit` and `/attest`, invokes the actual S175 Node evaluator separately, compares independently computed `inputHash` and `resultHash` to original S208 prepare record, then stores both hashes with target commit in SQLite. Missing or conflicting result evidence is rejected. Floor still issues durable signed mTLS ACK.

**Runnable exact-tested ZIP:** `SHEET217-independent-target-execution.zip` — 78,869 bytes, 57 files, SHA-256 `da094bd0cb3ddb98336c9bbbdb7343705e5dc1fea11d2bcbe03cc6a6c25a958d`. Includes `execution217.py`, `execute217.js`, `authority217.py`, `gate217.py`, `gate217_integration.py`, original WAL sources and dependencies. Run three gates from extracted root.

**Scope:** Reuses S175 evaluator for a separate execution, not independently derived math or formally verified semantics. Client provides `op,input`; authenticated input provenance and audit remain open. Same-host test PKI, non-atomic WAL/SQLite, no cross-host/power-loss production test. Next S218: authenticated durable input provenance, hash binding, and replay-tested target input selection.
