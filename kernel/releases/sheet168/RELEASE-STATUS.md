# SHEET 168 — Cross-Process Quorum Recovery (Prototype)

## Local verification
- New focused gate: **22/22 PASS** (`node gate168.js`).
- Inherited SHEET 167 focused gate: **20/20 PASS** (`node gate167.js`).
- Tested three distinct Ed25519 witness processes on TCP loopback with one witness killed and a two-vote quorum still accepted.
- Contradictory proposal was rejected by a durable signer vote lock.
- Durable observation snapshot, signed quorum checkpoint, rollback floor mismatch, and crash after external floor persistence were checked.

## Archive
- `SHEET168-cross-process-quorum.zip`: SHA-256 `e6e5eab8ef4e6542a7c73732ac9888c205bb640448933b7f66045d07a58ede63` (8,146 bytes); provided as a separate conversation artifact.
- Contents: `quorum167.js`, `runtime168.js`, `witness-server168.js`, `gate168.js`, `README.md`, `KERNEL-ASCII.txt`.

## Important boundary
**This GitHub commit records the prototype status; the executable files are in the downloadable ZIP, not yet published into the repository.** All three witness processes were on one host. TCP loopback test transport is not mTLS. Matching signed votes do not establish full distributed consensus, partition safety, or independent throughput attestation. SHEET 166 live mTLS runtime and Merkle-root verification were not integrated or rerun. Full historical regression tests were not rerun. Local checkpoints require an independently protected external anti-rollback anchor for strong security.

## Next
SHEET 169: authenticated cross-host transport and independent anti-rollback anchor; certificate-gated policy switchover against real recovery runtime; partition/fork testing.
