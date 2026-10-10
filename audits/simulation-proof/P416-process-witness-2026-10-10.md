# ROOT0 P4.16 authenticated process witness — 2026-10-10

## Executed result

Node.js v22.16.0, final local run: **18/18 assertions PASS**, 110.445 ms elapsed including child process start, SIGKILL, and restart. Process-local witness uses a Unix-domain socket, Ed25519 authenticated client requests, signed witness checkpoints, and SQLite WAL/FULL monotonic epochs.

20 simultaneous conflicting epoch-2 write requests: exactly 1 new accepted state and 19 denied as forks. Invalid signer, replayed nonce (within process), stale epoch, epoch gap, and unauthorized recovery requests were rejected. An authenticated RECOVERY_REVIEW request is acknowledged for manual independent review but makes no state change. Witness outage fails closed. Real SIGKILL test confirmed the persisted latest epoch survives witness-process termination and restart.

## Bugs and explicit boundaries

After SIGKILL, the server's stale Unix socket pathname caused a restart bind error (EADDRINUSE). Fixed the **test harness restart** by removing the stale pathname after process death and before server relaunch. **Production-safe socket recovery and ownership checks are not implemented.**

Other limits: nonce replay cache is only in memory and is reset after service restart; the private witness key and SQLite database remain on the same host; coordinated rollback remains possible. This is not hardware rooted or remotely independent time validation. No physical clock calibration or Planck-scale measurement.

Runnable exact source and dependencies are available in the P4.16 ZIP distributed in conversation. This GitHub commit stores the audit, **not yet the executable implementation**. SHA-256 of packaged ZIP: `f04ce03db77f9d20a986fe0b379eebe250ecefc114e823f542327585b5ec6f99`.

Next P4.17: durable nonce ledger, authenticated independent host witness, protected socket ownership and explicit cross-store rollback tests.