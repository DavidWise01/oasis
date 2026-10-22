# Step 16 — authenticated peer message model

Run `python3 docs/y2038/step16_auth.py`. Locally checked 8/8 passes for authenticated members, replay protection, tampered payload rejection, nonmember rejection, term advancement, stale term rejection, monotonic sequence and delayed message replay rejection.

Canonical JSON message envelope: `{body:{sender,term,sequence,payload},tag}`. A per-member demonstration HMAC-SHA-256 key authenticates an envelope. Term and last sequence are maintained in memory.

**Important boundaries:** The keys are deterministically derived demo fixtures and must never be used for deployed security. There is no network transport, mutual TLS, certificate identity binding, membership changes, persistent anti-replay state, key rotation, or secure secret provisioning. Crash/restart may reset replay protection. HMAC demonstration does not establish consensus correctness. Implement TLS 1.3 with mutual certificates and strict node identities, persist replay state, and use joint-consensus membership changes in a full Raft implementation.

Next: Step 17 snapshot/compaction/restore with committed-index integrity.
