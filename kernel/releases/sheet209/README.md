# SHEET 209 — Serialized Epoch Revocation

Local executable gate **15/15 PASS**: S208 stale epoch-1 token rejected after epoch 2 rotation; owner rotation blocked while original S208 Node WAL invocation holds the SQLite `BEGIN IMMEDIATE` transaction; epochs 1/2/3 tested, final WAL four commits, nonce replay and bad paths denied.

**Security boundary:** success applies to the controlled Python S209 entry point. Original S208 and legacy S176 Node writer can still be invoked directly. SQLite and WAL are not atomically committed; no remote-host, power-loss or cross-process isolation proof. A crashed writer may leave an orphaned WAL append requiring quarantine. S209 is a working mitigation, not yet complete mandatory internal fencing.

Run `python gate209.py` using the complete downloadable artifact containing dependencies and the exact tested gate. Next S210: remove untrusted legacy WAL entry points using OS permissions or a single privileged writer service, and SIGKILL test WAL/SQLite uncertain intervals.
