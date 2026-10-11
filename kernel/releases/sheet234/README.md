# SHEET 234 — Live mTLS Target/Floor to Hardened Broker

**Executed gate: 23/23 PASS** on Linux. The test launches the S233 hardened Unix broker as dedicated daemon UID with private SQLite, calls real S215 target and floor HTTPS endpoints using mutual TLS with correctly validated ephemeral test CA certificates, and passes the **unchanged** target/floor Ed25519 receipts into the broker. New broker234 verifies that original signed owner and epoch exactly match current owner alongside S228 hash-chain, WAL tail, nonce, generation and receipt signature checks. Forged signatures, absent client TLS certificates, wrong UID, stale bind and repair replay are rejected. Recovery updates exactly one broker generation and binding.

Full runnable release: `SHEET234-live-mtls-broker-authorization.zip` (14 files, 22,626 bytes), SHA-256 `4e0663eacca61798f9b6766a327786ea29dcccc278be6f015313eca30f2bd2f1`. Exact `gate234.py`, `broker234.py`, `server234.py`, S215 mTLS servers and dependencies are in the ZIP.

**Limits:** Same-host generated fixture certificates/signers and fixture-written WAL, not the full independently executed S179 target path. No remote production identities or cross-store atomicity and power-loss tests. Root test harness adjusts Unix socket group access. This is local integration only.

**Milestone progress: 90% = 9 of 10 explicitly tracked local engineering demonstrations**, not production readiness. Remaining milestone: cross-store crash/partition consistency and recovery validation. Next S235: fault injection at broker/floor uncertainty boundary plus strengthened WAL prepare digest validation.
