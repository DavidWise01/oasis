# Z333 — Tritritrium (Ttt): signed independent-key witness

Classification: MN PRIME/OCTAVIA Layer 1 software experiment only; not a physical chemical element. Frozen KET unchanged.

## Protocol
- 24! rank ledger uses canonical SHA-256 linked entries.
- Checkpoint payload contains schema, count and ledger tip.
- A separately generated Ed25519 witness signing key signs the checkpoint plus epoch.
- Verification uses public key, full ledger, and an independently trusted minimum epoch.
- Ledger and witness are serialized as distinct files.
- The optional chromium Cr24 3×8 address overlay is kept separate from physical Cr chemistry and from 5/3/1 governance and 3/1/2 RGB occupancy.

## Actual execution
`python test_z333.py` executed locally on 2026-10-18: **20/20 PASS**. Five ledger records. Negative tests include different verifier key, corrupted signature, tampered checkpoint count/tip, truncated/extended/reordered/edited ledger, invalid index, and old epoch.

## Limitations
'Independent' means a distinct ephemeral signer key and locally separate witness file within a single process/machine. No network witness, external trust anchor, process-kill power-loss, secure key custody, witnessed timestamps, or production assurance is established. Signature verification demonstrates provenance relative to a trusted public key, not truth of recorded statements.

Next Z334: freeze and audit this bounded recovery substack, avoiding unnecessary speculative expansion.
