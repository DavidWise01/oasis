# ROOT0 P3.21 — Phase collision and append-only integrity audit (2026-10-09)

## Phase and scattering audit
Replicated the exact P3.20 gate and residue equations independently in a JavaScript execution environment. 25,000 deterministic pseudorandom three-port complex states passed normalized-energy and full inverse checks. Maximum absolute norm discrepancy 7.993605777301127e-15; maximum single-component recovery discrepancy 3.219646771412954e-15. Changing the coordinate-bound residue by +1 caused different recovered amplitudes in all 25,000 sampled cases (not a cryptographic guarantee). All 1,000,000 seed values with otherwise fixed dimension, quad and coordinates map to all 65,521 modular residues, yielding 934,479 reused phase assignments, with 15 or 16 seeds per residue. The *full address* remains distinct.

## Append-only packet integrity
Added `p321_integrity.mjs` and `test_p321.mjs`. Each ledger entry stores sequence index, previous SHA-256 hash, canonical JSON serialization of the full address plus three complex channels, and a SHA-256 hash of these fields. Locally executed Node.js v22.16.0 test: 10,000 appended events PASS, payload tampering and interior deletion detected, hash alteration detected.

**Important limitation:** tail truncation of the ledger can still be internally valid; to detect it, anchor the latest head externally in an independent trusted record. SHA-256 chaining does not prove authorship or authenticity against an adversary able to rewrite the whole chain; use authenticated signatures or trusted checkpoints for that. The code validates payload structure, not the full P3.18 hierarchy grammar: callers should use that parser before appending.

These are symbolic mathematical information-flow and integrity tests, not proof of physical Dyson capture or Planck-scale access. The P3.7 voltage wrapper remains unchanged. Independent numerical equations were exercised, and ledger JS source was run locally. The exact committed P3.20 dependency tree and GitHub remote CI remain unverified.

P3.22 next: bind egress to an externally anchored ledger head, add signature verification and explicit retained-port integrity checks, then run end-to-end test from P3.18 address to P3.20 transport to P3.21 ledger.
