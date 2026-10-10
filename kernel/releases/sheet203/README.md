# SHEET 203 — Target-Owned mTLS Floor Closure

**Actual local execution:** `python gate203.py` 16/16 PASS. Original S176 Node WAL, S179 SQLite committed row, independently generated S201/S198 receipt over S202-derived mTLS service, and S195 floor authority signed ACK were tested in one integration gate. Target determines cursor from its own database; caller is limited to `resource` and `nonce`. S195 separately verifies 2 signed repair votes and persists generation and signed ACK. Repeated request/status lookup yield same ACK. Rogue certificate, forged input, torn WAL and missing target denied.

**Full runnable source ZIP:** `SHEET203-target-floor-integration.zip` (61,252 bytes), SHA-256 `feccd404d56a5f20d97a026da386b1297464a379e6cc1afa64f054b4246c5728`. Includes `gate203.py`, `service203.py`, S176 Node runtime, S179/S198/S199/S201/S202 and S193–S195 dependencies. ZIP is the exact tested layout.

**Boundaries:** target and floor are threads on one physical host; proof reads WAL and SQLite without a single shared transactional snapshot. Synthetic keys. No production remote host, cross-store atomic commit, power-loss, partition, hard-kill or full historical regressions. Existing floor remains durable after later WAL corruption; target rejects new proof lookup but this gate is not retrospective revocation.

Next SHEET 204: consistent WAL/target snapshot and freshness-bound floor approval with process crash tests.
