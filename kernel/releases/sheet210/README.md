# SHEET 210 — Single-Writer WAL Crash Quarantine

**Executed locally:** S210 **12/12 PASS**, inherited S209 **15/15 PASS**. A Unix-domain socket service invokes the original signed S208 Node WAL runtime while holding a SQLite BEGIN IMMEDIATE owner check. Socket mode is 0600. WAL is hash-chain verified before append and the new head is bound to SQLite afterward.

**Actual SIGKILL:** service is killed after WAL append and before SQLite commit. On restart, the additional WAL tail is detected as UNBOUND_WAL and subsequent writes are rejected without truncation or fabricated acknowledgment.

**Executable package:** `SHEET210-single-writer-crash-quarantine.zip` (43,546 bytes); SHA-256 `c489e3c0aa59617f6df5a0fd3b2acbe159dd8dd5371ee736681084d573d6b474`. Includes `service210.py`, `gate210.py`, preserved S209/S208 Node modules, and README. This GitHub commit is a release record only; executable source is in the ZIP.

**Security boundary:** Permission 0600 on the socket does not prevent same-UID users from invoking the old writer directly. OS-user and filesystem isolation are NOT implemented. The service and WAL share one host. The SQLite/WAL commit is NOT atomic. This is a local fail-closed recovery test, not distributed exactly-once proof.

Next S211: dedicated OS service identity and restricted WAL directory, then post-crash signed floor reconciliation.
