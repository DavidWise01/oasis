# SHEET 212 — Dedicated OS Identity Writer Gate

**Executed locally:** 14/14 PASS (`python gate212.py`), Linux root setup, service executed as UID `daemon` while adversarial client ran as `nobody`. Actual S210 service and original signed S208 Node WAL worker were used. Owner-scoped 0700 WAL directory and 0600 WAL/socket reject different-UID legacy bypass and socket use. SQLite epoch rotation rejects stale owner. Real SIGKILL after WAL commit, before SQLite head binding, leaves an orphan; service restart quarantines it without altering WAL history.

**Full runnable source and test:** `SHEET212-dedicated-writer-isolation.zip` (46,586 bytes), SHA-256 `c2cc3cf43478f097f59a43eeea94d5ac247d00935ca59bad7fc9126a97b7084a`. Includes `sheet209/gate212.py`, S210 service and preserved S208/S209 Node runtime.

**Boundary:** Root and service-same-UID writes can bypass file DAC; no cross-store atomicity or hardware protection. Signed orphan repair remains **not integrated** and quarantine is deliberately maintained. No mTLS or cross-host authority, power-loss or full historical regression. GitHub commit is release documentation; executable code is in the ZIP.

Next S213: independently signed orphan repair with target receipt and signed monotonic floor, under the isolated service identity. Prove that unverifiable orphan never leaves quarantine.
