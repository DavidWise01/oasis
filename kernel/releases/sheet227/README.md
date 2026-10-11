# SHEET 227 — Control DB Role Broker

**Focused local gate: 22/22 PASS.** New Python Unix-domain broker uses `SO_PEERCRED` to authenticate actual Linux caller UID and allows operator ownership rotation, writer binding and repair floor-binding transitions under a single SQLite `BEGIN IMMEDIATE` serialization boundary. 12 simultaneous writer bind attempts returned exactly 1 winner, 11 stale rejects. Audit table records five accepted mutations. Wrong-role, stale owner, replay, invalid floor and extra request fields rejected.

**Verified ZIP** `SHEET227-control-db-role-broker.zip` (122314 bytes), SHA256 `e682eebd9b8f4c9b399dd205f842593146d80fd5b705c3eea3e5fa0fb4614363`; contains `broker227.py`, `gate227.py`, `README-SHEET227.md`, nested `S226-baseline.zip`. Run `python gate227.py` on Linux with suitable privileges.

**Security blocker:** Repair broker presently trusts `approved: true` from repair UID; broker does NOT verify cryptographic signed target/floor evidence, and does not independently verify WAL head. Database is not yet isolated by OS permissions from all client UIDs. Do not deploy as a replacement for S226. S226 42-check integration was NOT rerun this turn. Next S228 should move S226 cryptographic repair validation and WAL binding checks into broker; restrict DB direct access; rerun full recovery.
