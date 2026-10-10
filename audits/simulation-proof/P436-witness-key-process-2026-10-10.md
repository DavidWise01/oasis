# ROOT0 P4.36 — process-separated witness signing (2026-10-10)

Local Node.js 22.16.0: **19/19 regression assertions PASS**, measured **81.455 ms**. A child-process signing service loads the Ed25519 witness private key from its own directory and signs domain-separated checkpoint receipts; controller uses pinned public key to verify. Test covered signed receipt, altered nonce/epoch/head, wrong deployment and signing key, invalid request input, 20 parallel requests, SIGKILL/outage fail-closed and restart. Controller instance holds no private key.

Prior P4.35 workflow commit `c72366b8a4da6b8897528570d889efc07f16019b`: workflow-run query for this commit returned no associated PR runs and combined commit status returned no statuses. **Hosted CI success NOT VERIFIED**. Local source-isolation regression passed in P4.35.

**CRITICAL:** This is a key handling *demonstration*, NOT a secure history authority. Child signer accepts arbitrary syntactically valid future epochs and does not enforce CAS monotonicity. It MUST be gated by P4.34 StrictCasWitness before any deployment. Process and private key are on the SAME HOST and run as same OS user; 0600 key permissions do not isolate from same user or administrator. Coordinated rollback, hardware-rooted custody and genuine remote trust domain remain unresolved.

Exact executable source/regression and JSON packaged as `p436_bundle.zip`, SHA-256 `e1667a0c2c4631bb89554b82d4a9a678f825f2b8dcd56d7e68ea5cee09135e37`. GitHub contains P4.36 controller and signing process source; test remains in ZIP.

Next P4.37: integrate P4.34 CAS validation inside signing service and refuse forged/future epochs, then test process restart and replay.