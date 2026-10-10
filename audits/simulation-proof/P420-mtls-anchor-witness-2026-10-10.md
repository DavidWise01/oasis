# ROOT0 P4.20 — TLS 1.3 mutual-authentication test (2026-10-10)

## Executed benchmark
Node.js v22.16.0, OpenSSL 3.5.5: **17/17 assertions PASS**; final local rerun **773.831 ms** including generating ephemeral CA, test certificates and process restarts. Twenty conflicting checkpoint writers yielded **1 accepted and 19 rejected**. Witness preserves nonce replay ledger and epoch under two SIGKILL/restart cycles, refuses stale epoch, rejects rogue/incorrect-role client certificates, and requires separate Ed25519 request signatures. Signed administrator RECOVERY_REVIEW is non-mutating. Network outage fails closed.

## Fixed during execution
A rejected TLS connection caused unhandled `ECONNRESET` on the server TLS socket, crashing the process. Explicit socket error handler added, regression rerun successful.

## Limits
Service and controller are two processes on the SAME HOST; TLS endpoint uses loopback, not separate machine. Test CA and private keys all reside in a shared temporary directory. Certificate CN-based roles are provisional, not production authorization. An attacker with host control can roll back witness SQLite and controller together; no nonrollbackable hardware/remote anchor has been demonstrated. Precise symbolic 10^-36-second clock is unrelated to physical metrology here. No power-failure test.

Complete executable files with regression harness and results are in chat ZIP `p420_bundle.zip`, SHA-256 `f44f8b8743ff643d3f0ba3419061a261783cd388b864ce68d2a77a4c3f7aabeb`. GitHub audit commit does not include new executable source.

Next P4.21: independent deployed witness host, separate CA/key custody, durable monotonic external anchor and cross-site rollback exercise.