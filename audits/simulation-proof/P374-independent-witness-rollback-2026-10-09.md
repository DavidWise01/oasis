# P3.74 — Independent witness rollback verification (2026-10-09)

User topology: `-+5 + 1`. P3.74 uses a separate **in-memory** checkpoint witness. Ed25519 authenticates the authority's published epoch/count/hash; the witness rejects older checkpoints and same-epoch divergent commitments. The checker compares the local checkpoint with the witness and validates the SQLite database's internal integrity and current checkpoint against the witness.

Local executed Node 22.16.0: PASS 12 assertions. An old SQLite snapshot was restored together with its matching old signed checkpoint; the retained independent witness correctly rejected the dual rollback. Wrong signature, old publication, and temporarily unavailable witness also failed closed. Local scalar-0 and photon geometry are unchanged.

**CRITICAL LIMITS:** This witness is volatile and can be rolled back, restarted, or replaced. The test *assumes* its state survives local database rollback. The publish/commit ordering and independent atomic durability are not solved. A genuinely nonrollbackable external witness and an authenticated publication workflow are still required. Signature freshness is not guaranteed if the witness loses its state.
