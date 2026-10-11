# ROOT0 P4.45 — Cross-UID atomic witness service (2026-10-10)

Executed on a Linux root-enabled container using Node v22.16.0 and `setpriv`. **13/13 assertions PASS**, final rerun **388.974 ms**.

Witness service ran as UID **65534**, controller requests as UID **33** with shared GID 65534, and unauthorized UID/GID **1000/1000** could not connect to the 0660 Unix socket. Witness key and SQLite database stayed in witness-owned mode-0700 directory: direct reads from controller UID failed. An Ed25519-signed administrator policy installed; cross-UID signed READ and signed CAS epoch 1 succeeded; repeated request rejected; repeated/old CAS epoch rejected. Real SIGKILL caused outage to fail closed; witness restarted with retained history and rejected the consumed nonce. The stale socket was removed explicitly in the trusted *test harness*, not opportunistically by an unauthenticated request.

**Limits:** Two OS identities share one Linux kernel and root administration. A host-level root compromise or coherent rollback of database and keys remains possible. Socket permissions are filesystem access control, *not* proof of application authorization; signed requests are still required. The test-created admin policy endpoint is accessible over the Unix socket and requires its own signature. The `reclaimStaleSocket` option must only be enabled by a trusted supervisor after verifying no live server; its UID check alone is not safe against an active same-UID listener. Node SQLite remains experimental.

The committed P4.45 service imports `p443_atomic.mjs`, which is included in the ZIP but not yet aligned into the GitHub repository. Accordingly this is **not** a self-contained GitHub release. Test source and recorded results are also in ZIP.

ZIP SHA256: `d9d44fa20d8e7dd7f063f65902d5c7b05c3a7a549a2697b03af66f6de137b9dc`.

Next P4.46: synchronize P4.43 dependency and P4.45 regression to GitHub; validate real CI and build a hardened supervisor with reliable stale-socket lifecycle handling. Independent host trust boundary still unimplemented.