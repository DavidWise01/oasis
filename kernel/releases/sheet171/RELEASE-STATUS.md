# SHEET 171 — Source-Signed Recovery Anchor Prototype

New checks: 21/21 PASS (`node gate171.js`). Inherited SHEET 170: 20/20 PASS.

Implements an isolated-process anchor authority with independent Ed25519 key, source-signed recovery cursor (resource, rows, Merkle root identifier, source sequence), 2-of-3 witness certificate verification, monotonic persistent decision floor, stale-checkpoint quarantine, and an outage fail-closed test.

Archive: `SHEET171-source-signed-anchor.zip`, 14232 bytes, SHA-256 `0d7548db38dcb45819bc819a58efcfd6345405dc848a79a3dc79f8984ee70d1a`. Full runnable source and inherited SHEET 170 code are in the conversation ZIP; this commit records the report only.

Verification boundary: all processes use the same physical host; test RPC is localhost TCP without mTLS. Private fixture keys are exported to local test configuration. Source-signed root is checked by identity but independent Merkle proof validation is absent. No real cross-host network partitions, protected remote signer hardware, SHEET 166 live mTLS/Merkle pipeline integration, or full historical regression run.

Next SHEET 172: cross-host mTLS identity gating, harden anchor key storage, validate source Merkle proofs, test live source/target recovery and partitions.
