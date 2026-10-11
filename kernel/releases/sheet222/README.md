# SHEET 222 — Dedicated-UID mTLS Orphan Recovery (Integrated)

**Executed on Linux as root:** `python gate222.py` — **30/30 PASS**, rerun after packaging. Actual S220 socket writer runs under Linux `daemon`, invokes S208 Node WAL with issuer-signed S218 input; `nobody` is denied direct WAL read. Real SIGKILL after WAL persistence but before SQLite binding leaves an orphan that blocks further protected writes. The S218 target mTLS service verifies ledger-backed execution and stores its own commitment; separate floor mTLS service verifies the target signature, issues a durable signed Ed25519 floor ACK, supports retry and `/status` after restart. S213 reconciliation rejects forged receipts/replay, binds exact WAL head, and the daemon writer resumes through the same socket.

**Full exact-tested source:** `SHEET222-dedicated-uid-mtls-recovery.zip` provided in conversation, 73 files, 102,671 bytes, SHA-256 `8e51fbc95ca83bd80f3d19f4215d77cb99501120bab92d7262537a31d5a33725`. `gate222.py` is included in ZIP along with all predecessor source, cert fixture generation, target/floor endpoints and tests.

**Limitations:** The reconciliation operation is invoked by the root test harness, not through an isolated unprivileged authorized repair service. Target and floor run as local threads with fixture-generated CA and keys. Same-UID/root bypass and WAL-SQLite cross-store atomicity remain open. No remote hosts, network partition, physical power failure, or full production PKI validation. New combined gate is local end-to-end integration; don't count prior independent suites as combined tests.

Next S223: repair service privilege isolation, signed approval storage and crash recovery during reconciliation.
