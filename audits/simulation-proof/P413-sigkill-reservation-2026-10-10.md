# ROOT0 P4.13 — Actual process kill at genesis reservation (2026-10-10)

Node.js 22.16.0 local rerun: **11/11 assertions PASS**, elapsed **49.181 ms**. A forked child persists a deployment reservation then sends a message to its parent. Parent sends actual `SIGKILL` and observes a SIGKILL process exit. Restart inspection reports `QUARANTINE / reserved-without-authority`. Reattempting the same grant returns `deployment-already-reserved`. Ed25519-signed `REVIEW_REQUIRED` intent is verified against the reservation digest, but does **not** automatically undo it or provision a new genesis. Tampering and mismatched signer are rejected.

Committed runnable dependencies: `p410_genesis.mjs`, `p412_deployment.mjs`, `p413_recovery.mjs`, `p413_worker.mjs`, `test_p413.mjs` under `docs/reality-tensor/dyson-inversions/`.

Scope limits: This test terminates after the reservation is durably synchronized and the parent receives acknowledgment; it does not test killing at arbitrary instruction boundaries, filesystem corruption or physical power loss. The provisioned local registry is not independently attested. An erased reservation may look uninitialized, and coordinated rollback remains undetected without an external monotonic witness. No automatic recovery is provided. Clock and geometry model are unchanged; this is a storage-security regression rather than physical time validation.

Next: P4.14 randomized kill-point matrix and real separate-process trusted witness protocol with authenticated intent.