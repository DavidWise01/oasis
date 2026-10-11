# SHEET 242 — Overlapping Committed-Orphan Recovery

**Fresh local results:** S242 36/36 PASS; S241 21/21 PASS; S240 14/14 orchestrator checks with 53/53 nested branch checks. Total 124 checks across these independently run suites (some conceptual test coverage overlaps).

The original S176 Node writer produces a committed WAL; the target and floor mTLS authorities persist signed receipts, then both authority processes are SIGKILLed before ACK transport. An outage-time floor status request fails. After both services restart, identical target and floor signed receipts are retrieved. Broker verifies the unchanged Ed25519 approval and WAL binding, commits once, then survives a separate SIGKILL/restart with monotonic floor generation and replay rejected.

Executable ZIP `SHEET242-overlapping-committed-orphan-recovery.zip`, 80,147 bytes, 55 files, SHA-256 `2858363aa496b5686356f5775865c99599ffa95722128d03dc0c99f35a26cf84`. Includes `gate242.py`, `gate241.py`, `gate240.py`, original `s176/` Node runtime, mTLS servers, broker, tests and instructions. ZIP integrity passed.

**Limitation:** Target/floor deaths overlap; broker is killed later. No simultaneous three-service death, network partition, physical power loss, real independent hosts, or cross-store atomicity proof. Locally generated test CA. Milestone score remains 90% (9/10 local engineering milestones), not production readiness.

Next SHEET 243: concurrent broker/target/floor uncertainty window, ACK-loss, restart, and partition simulation with independently checked final WAL and floor histories.