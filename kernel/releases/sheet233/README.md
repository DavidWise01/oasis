# SHEET 233 — Hardened broker Unix socket

**Executed:** S233 18/18 new checks; S231 17/17; S230 16/16; S228 18/18. Total **69/69 focused checks PASS**.

Hardened broker UID 1 test used mode 0710 socket parent, socket mode 0660, SO_PEERCRED, max request 4096 bytes, one-second incomplete request timeout, and a capacity-16 bounded worker pool. Unauthorized writer/repair clients without group access are denied at the filesystem. Broker remains owner of its private SQLite directory. No malformed or oversized request advanced state.

**Exact executable ZIP:** SHEET233-hardened-broker-socket.zip (18,458 bytes, 13 members); SHA256 e0ac04366650d1d0543566dcbf764f67f9a4984c11c8dff54228bdf0cf448f46. Contains gate233.py, hardened server233.py, inherited regression gates, and docs.

**Project milestone progress: 80% (8/10 explicitly tracked engineering milestones)**, not production readiness. Remaining: authenticated live mTLS-to-broker integration and cross-store crash/partition durability validation.

**Limitations:** Explicit group policy must be configured to permit legitimate writer and repair UIDs to connect; the new test deliberately denies them. Live mTLS integration not executed; prior source is a focused broker prototype. No cross-store atomicity, root/same-UID bypass protection, remote fault injection or production PKI.
