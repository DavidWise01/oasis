# SHEET 247 — FULL-Sync Crash Recovery Checkpoint

**Executed local gates**: S247 21/21 PASS, inherited S235 15/15 PASS, inherited S246 39/39 PASS. **75/75 across three separately run suites.**

The new gate runs broker Ed25519 dual-signature repair with SQLite WAL journal and PRAGMA synchronous=FULL, terminating subprocesses at the COMMIT boundary via hard exit. Precommit crash rolls back the binding and floor; signed retry succeeds once. Postcommit crash preserves both. Replay rejected. Database integrity verified; original hash-linked WAL remains byte-identical. The separate S246 regression tests a localhost TCP-isolation proxy and 12 authenticated floor ACK retries. Inherited source needed extracted file read permissions restored for the daemon-UID broker; the release archive packages normalized readable modes.

**Exact executable release**: `SHEET247-full-sync-crash-checkpoint.zip` (98,330 bytes, 67 files), SHA-256 `fa2bd31b90ec55bdf221df925ada3381ad64c01ac89015ff304aaba259bc66ba`. Contains new `gate247.py`, S235/S246 gates, original S176 Node writer and inherited live mTLS services and broker. ZIP integrity passed.

**Not demonstrated:** Actual cross-host partition, hardware power-cut, storage-controller flush persistence, independent quorum, cross-store atomicity, adversarial same-UID process. SQLite FULL sync checks are local process-crash durability evidence, not proof against hardware power loss. Network namespaces remain unavailable.

**Milestone progress:** **90% (9/10 local engineering demonstrations)**, not production-readiness. Next SHEET 248: portable two-host partition and physical-power-fault test harness with independent evidence verification.