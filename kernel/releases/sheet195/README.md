# SHEET 195 — Authenticated Target Receipt & Lost-ACK Recovery

**Executed locally:** 17/17 PASS (`python gate195.py`). A mTLS floor service independently queries a separate mTLS target-receipt endpoint, checks target Ed25519 signatures and two repair votes, enforces certificate fingerprint to resource scope, and atomically retains the signed floor ACK in SQLite. A deliberate post-commit lost acknowledgment is resolved by a signed status lookup; exact retries do not advance generation. Missing target receipt, rogue client, forged vote, fork, and authority outage fail closed.

Executable ZIP: `SHEET195-authenticated-receipt-recovery.zip`, **9702 bytes**, SHA-256 `0db968e2b3e6d97a2e5cbb5e2d3543020969a11cff297dfe67281a7d31c78fad`; includes `authority195.py`, `gate195.py`, inherited `authority194.py` and `authority193.py`, README.

**Verification boundary:** services are separate HTTPS **threads on one host in one process**, not independent hosts. All keys and receipts are synthetic fixtures, not sourced from independently durable target commits. No S176 WAL / S190 live repair integration, power-loss or SIGKILL recovery, cross-host partition or historical regression. Source remains available in the ZIP; GitHub update is a release record only.

Next S196: independent subprocess hosts for target and floor, durable target-side request receipts and post-commit SIGKILL, plus multi-resource replay tests.
