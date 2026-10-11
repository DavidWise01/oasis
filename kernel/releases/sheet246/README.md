# SHEET 246 — TCP Transport Isolation and Concurrent ACK Retry

**New gate:** `python gate246.py` 39/39 PASS. **Inherited S245:** 32/32 PASS. **71/71 assertions across separate runs.** The live floor mTLS authority persists a signed Ed25519 ACK while the client loses the transport connection. A new TLS-transparent loopback TCP proxy denies requests during an outage; after healing, 12 concurrent authenticated `/status` retries return the same original signed ACK. The broker accepts one repair and rejects replay. Original S176 Node WAL writer and target/floor mTLS are in the executable release.

**Exact verified ZIP** `SHEET246-tcp-partition-concurrent-retry.zip`, 95,659 bytes, 65 files, SHA-256 `d3513db66a47c4507fb3444706b48dc018cab06410a2f7a826bed152d44ea028`. Contains the tested `gate246.py`, `proxy246.py`, predecessor gates and original Node/WAL runtime.

**Limits:** Linux network namespaces could not be created (`Operation not permitted`); this is a local TCP relay outage, not independent host or packet-filtered network partition. No physical power-loss, durable cross-host consensus, or atomic WAL/SQLite commit proof. **Milestone progress 90% (9/10 demonstrations)**, not production readiness. Next S247: true multi-host partition/privileged netns test, plus durable power-loss recovery evidence.
