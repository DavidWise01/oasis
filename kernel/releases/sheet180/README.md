# SHEET 180 — Signed Target Heads & Reconciliation

Local test gate: 25/25 PASS (`python gate180.py`). Implemented Ed25519-signed target heads binding resource, owner epoch, cursor, and SQLite SHA-256 append chain; rejects signature fraud, stale checkpoints, mismatched WAL fixtures, uncertain prepares, and conflicting retries. A child exits with status 137 after durable target commit, and the durable request ID reconciles the lost acknowledgment.

Release ZIP: `SHEET180-signed-target-reconciliation.zip` SHA-256 `b138e590446b44647c3ecb731b0a2d5d26d5f65cafe6e4cd09cc8eedb3bbb525`, contains the exact tested `signed180.py`, `atomic179.py`, `gate180.py` and README.

**Boundary:** GitHub source is a compatible implementation of signed180, while the ZIP is the executable tested fixture. The new GitHub source requires `atomic179.py` from the ZIP. Local WAL fixture not a live S176 bridge. Signing happens AFTER SQLite commit and is not atomic with it. No independent host, real remote anchor or cross-host proof. No full predecessor regression run for S180.
