# SHEET 221 — Dedicated-UID Signed-Ledger Writer

**Actual new gate**: `python gate221.py` **19/19 PASS** (Linux root test harness; service runs as `daemon`, adversarial process as `nobody`). Actual S220 Unix socket and S208 signed Node WAL execute under `daemon`, with file/directory modes `0600`/`0700`. `nobody` cannot connect, read input ledger/WAL, or append using legacy Node. Signed registered input commits; unregistered, tampered, duplicate nonce, caller-injected input, and stale owner are rejected. Two authorized WAL commits.

**Limits:** This is OS identity isolation for different UIDs only. Root/same-UID access can bypass. Not an independently deployed target/floor recovery path; no remote mTLS at the same time as dedicated UID, no cross-store atomicity. Complete test source is packaged in conversation release ZIP.

Next S222: bring live mTLS target/floor protocol into the protected service workflow and test crash + signed orphan reconciliation across process boundaries.
