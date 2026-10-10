# SHEET 170 — Signed Rollback Anchor Prototype

Verified locally: 20/20 new focused Node.js checks and inherited SHEET 169 gate 24/24 PASS.

The prototype implements an Ed25519-signed decision floor binding the recovery resource, signed 2-of-3 proposal hash, policy generation, committed cursor row count, policy mode, and supplied Merkle-root identifier. It rejects quorum forgery, duplicate witness votes, stale generation, cursor mismatch, false resource identity, wrong Merkle-root binding, local checkpoint mismatch, tampered observation and corrupted floor signatures.

Executable archive: `SHEET170-signed-rollback-anchor.zip` (8,297 bytes), SHA-256 `2077001d8f5125d5351fdb6ba2a584c86975c8ca13e70e83d2738f6c8dbfcaa6`. The executable source is provided as a separate download in the corresponding ChatGPT conversation; this commit documents results only.

Important limits: the external floor is in a separate local directory **on the same machine**, not an independently controlled physical anchor. No actual source Merkle proofs are independently verified, no SHEET 166 production recovery integration is tested, and cross-host partitions/byzantine consensus are not established. No full historical regression was rerun.

Next SHEET 171: external service anchoring on a distinct host and distinct key boundary, source-authenticated Merkle cursor validation, and network-partition tests.
