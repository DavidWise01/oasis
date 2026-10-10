# SHEET 167 — Decision Witness Quorum Prototype

Predecessor: SHEET 166 commit 47289e3. A separate local Node.js prototype has passed 20/20 focused quorum checks. The downloadable prototype package includes `quorum167.js`, `gate167.js`, README, and ASCII architecture.

## Implemented locally
- Three Ed25519 identities, 2-of-3 matching signature certificate validation.
- Durable per-witness same-generation vote locks (file fsync + directory fsync).
- Generation and previous-hash validation; mode/row consistency checks.
- Proposal binding to resource root and observation digest.
- 48-row dwell and cooldown preconditions.
- Test cases for duplicate votes, forged signatures, conflicting transitions, stale generations, and witness restart.

## Important release boundary
This status file **does not publish the prototype executable files to GitHub**. The executable files are available in the separate downloadable ZIP attached in the conversation. It is not a cross-host consensus implementation, not wired into SHEET 166 live mTLS recovery, and no inherited tests or Merkle recovery check were rerun. Full persisted hysteresis snapshot restoration and anti-rollback witness floors remain open.

Next gate: distribute witnesses across hosts and integrate quorum-confirmed policy transitions into actual mTLS recovery, with mutually authenticated replication and independent durable floors.
