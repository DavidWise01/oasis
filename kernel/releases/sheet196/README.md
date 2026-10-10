# SHEET 196 — Durable Target Receipt Crash Gate

Run `python gate196.py` from the accompanying ZIP (requires Python cryptography).

**15/15 PASS.** A separate local mTLS target subprocess atomically commits Ed25519-signed receipts into SQLite (`journal_mode=WAL`, `synchronous=FULL`). It intentionally exits with code 137 after the SQLite commit and before HTTP acknowledgment. Upon restart, the exact signed receipt is retrieved; duplicate commits are idempotent, contradictory receipts are rejected. A second persisted receipt survives SIGKILL and restart; unauthorized mTLS client and target outage fail closed.

**Executable archive:** `SHEET196-durable-receipt-crash.zip`, 10,387 bytes, SHA-256 `96f30c9c5876d66eeae6f52394268d0310886532aaf0fecd3be7a9d5bf51f1e2`. Includes `target196.py`, `gate196.py`, README and inherited S193–S195 service modules.

**Limits:** The S195 floor service was not run in this gate. Both services are not demonstrated as independently hosted remote processes. Keys and SQLite share the same host. Signed receipts come from synthetic commit requests, not the original S179 target writer. No independent rollback storage, full historical regression, physical power-loss, or partition proof.

Next S197: separate target and floor subprocesses with independently durable storage, live mTLS receipt lookup, and lost-ack hard-kill tests.
