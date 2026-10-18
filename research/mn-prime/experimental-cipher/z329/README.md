# Z329 — Tribinonium (Tbn)

**Classification:** MN PRIME / OCTAVIA Layer 1 simulated computational candidate, not a chemical element discovery. Chromium Cr24 is an optional symbolic 3×8 addressing analogy; 5/3/1 remains an independent KET/SAPPHON hierarchy. Frozen KET unchanged.

## Signed segment protocol
- 24 distinguishable addresses have 24! permutation ranks.
- Each record has a segment ID, monotonically increasing local sequence, rank, prior SHA-256 digest, and its own SHA-256 digest.
- Each segment has a signed checkpoint payload containing segment ID, record count, incoming and outgoing hash tips, current key ID, and prior key ID.
- Ed25519 signs canonical JSON.
- A change of key requires a separate rotation authorization signed by the previously trusted key, binding old and new public key IDs.
- Verification requires an independently trusted genesis public key and a known public-key registry.

## Executed test
2026-10-18: local test_z329.py — **20/20 PASS**. Three linked segments, ten records; authorized A→B rotation accepted and continuing B accepted. Negative tests cover rogue signers, tampered rotation authorization, wrong genesis signer, reordered/omitted segments, modified content/checkpoints and invalid 24! indices.

## Limits
This validates software consistency and local signature verification. It does not establish externally anchored identity, secure private-key custody, independent timestamps, revocation, anti-rollback relative to a trusted external state, or physical element properties. A holder of an authorized key may sign fraudulent content. No claim of quantum advantage.

## Next
Z330: signed checkpoint recovery after interruption, revocation policy and external trust-anchor interface, without changing the frozen kernel.
