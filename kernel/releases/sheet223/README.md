# SHEET 223 — Privilege-Isolated Repair Service and Crash Rollback

**Executed:** `python gate223.py` **37/37 PASS** with actual S220 daemon-owned WAL writer, real SIGKILL between WAL and SQLite, quarantine, authenticated ledger-backed mTLS target, durable signed floor ACK, and a separate daemon-run 0600 Unix repair socket. The `nobody` UID cannot access the socket. Forged target receipt rejected. An intentional repair-service SIGKILL immediately before SQLite `COMMIT` rolls back both head binding and repair-floor generation; restart with the same independently signed receipts succeeds, and writer resumes. Original WAL preserved without rewriting.

Exact tested archive: `SHEET223-repair-service-crash-rollback.zip`; **78 files, 112273 bytes**, SHA-256 `a243947c261dbd1b18f86e1269a4bc040aac8adc29b63960eea8531a2fae0ee4`. ZIP contains `gate223.py`, `repair223.py`, `reconcile223.py` and S222 dependencies. Verified `zipfile.testzip()` returned no errors.

**Limitations:** writer and repair services share `daemon` UID, so same-UID processes and root can bypass DAC. No network peer attestation at repair socket, no power-failure test, remote-host PKI, or cross-store atomicity. Crash injection is before COMMIT, not during disk/fsync.

Next S224: split repair UID with explicit restricted access and test crash-after-commit as well as precommit.
