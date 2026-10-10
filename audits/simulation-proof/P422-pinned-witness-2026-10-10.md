# ROOT0 P4.22 — signed witness receipt verification

Date 2026-10-10. Local Node.js v22.16.0 + OpenSSL. Reproducible test `node test_p422.mjs`: **19/19 assertions PASS**, final elapsed **867.111 ms**. PinnedWitnessGuard uses the configured witness Ed25519 public key to verify checkpoint (deployment, epoch, digest) before consulting controller local epoch/head. Additional tests reject tampered checkpoint digest, changed epoch, invalid signature, wrong deployment, and absent witness; inherited integration test checks controller-only rollback, witness SIGKILL restart, stale epoch rejection and non-mutating recovery review.

Source committed under `docs/reality-tensor/dyson-inversions/p422_guard.mjs`. Complete test runner and all required dependency modules are included in the conversation P4.22 ZIP (SHA-256 `ae8576d89bc7e3f991271d6b051ef79e79dfa85c59ebd35e645d9ecda1a4b4c9`), rather than a new external-host deployment.

**Open gap:** Controller and witness are separate processes on the SAME HOST. Private keys and local stores reside in shared test filesystem. In-memory `floor` is not durable across a controller process restart, and a coordinated rollback of all local stores is still undetected. This is not a real remote/witness-admin test nor antirollback hardware proof.

Next P4.23: deploy isolated external witness/key custody and durability; test rollback across independent host failure domains.