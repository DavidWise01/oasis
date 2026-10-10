# ROOT0 P4.15 signed witness prototype — 2026-10-10

Local Node.js v22.16.0 execution: **23/23 assertions PASS**, latest measured 12.7 ms. Separately stored SQLite witness uses Ed25519 authenticated (deployment, epoch, head) stamp and sequential epoch registration; operator's local authority tracks its independently hashed epoch/head. The verification gate fails closed on missing/outage witness, invalid signature, local rollback, local-ahead, and same-epoch fork.

| Test | Result |
|---|---|
| Witness missing, local present | quarantine |
| Witness signature alteration/wrong signing key | reject |
| Outdated witness publish and same-epoch fork | reject |
| External witness offline | block advancement |
| Restored older local DB with newer witness | detect rollback |
| Interrupted publication between local and witness | quarantine local-ahead |
| Restore BOTH coherent old SQLite snapshots | **undetected (critical gap)** |

The witness is an *additional local database* rather than an independently operated authority. A compromised host with storage snapshot capabilities can roll back both. There is no inter-database atomic commit; test's direct witness catch-up is an experiment, NOT authorized recovery and must be replaced with signed intent and monotonic independent audit. No network-isolated service, quorum, hardware monotonic counter, true process-level contention or power interruption has been validated.

Bundle of runnable source, local dependency, test, JSON and README is linked in current conversation. It is not guaranteed GitHub source checkout is identical unless source files separately committed. Next P4.16: isolate the witness into a distinct process, lock down signing authority, and add authenticated recovery intent plus fault injection.