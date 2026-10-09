# P3.57 Four signed witnesses, 3-of-4 quorum

Applied on top of P3.56: fixed domain context, signed checkpoint epoch/length/head, four distinct Ed25519 keys, require three distinct authorized signatures. Local Node.js 12 assertion test passed. Delayed one-witness delivery does not prevent quorum. Old epochs, duplicate votes, fewer than three, foreign checkpoint head or invalid signatures are rejected.

**Known limitation:** P3.57's `accept()` checks existing trusted head as a prefix and candidate terminal head but does not itself recompute intermediate SHA-256 chain links. Applications MUST first invoke full P3.55 chain verification and securely persist the accepted checkpoint and authorized public key registry; otherwise a forged intermediate record can evade prefix checks. No network consensus, Byzantine tolerance under multiple forks, or durability guarantee proven here. Next P3.58 integrate full-chain validation into accept, then test competing network partitions.
