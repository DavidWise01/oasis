# SHEET 228 — Cryptographically Verified Recovery Broker

**Local focused gate:** `python gate228.py` **18/18 PASS**. The repair path refuses S227's former caller-controlled `approved: true` field and instead checks two Ed25519 signatures (target and floor), bound resource/nonce/previous/new WAL heads and sequence positions, and the monotonic floor generation. It scans an actual two-record hash-linked WAL fixture for matching prepare/commit semantics and atomically updates SQLite binding, generation and audit event inside one `BEGIN IMMEDIATE` transaction. Ten parallel approvals: one accepted and nine rejected as stale.

**Exact executable release ZIP:** `SHEET228-cryptographic-recovery-broker.zip`, 129,137 bytes, SHA-256 `1227dfc4122b3eec69f2106b65e10d7dba17ed632fce5a56bbbda650bcf195da`. It contains `broker228.py`, `broker227.py`, `gate228.py`, documentation and the full earlier S227 archive.

**Limits:** This is a *focused broker security prototype*. Fixture WAL input and local keys, no live target/floor mTLS rerun, no separately committed S179 target record, no broker-exclusive OS DAC, and no physical-crash or distributed atomicity proof. Role authentication is performed by the inherited socket listener (SO_PEERCRED), while this focused gate invokes the broker method with test UID values.

Next S229: require independently generated target/floor receipts, restrict control-DB access to broker UID and exercise full S226 crash recovery end to end.