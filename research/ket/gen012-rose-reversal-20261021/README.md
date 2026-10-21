# Rose V4 — Reversal and deterministic replay

Builds on V3. Three weak windows **122–125, 140–145, 360–366** contain 17 slots and 14 adjacent transfer links. Each source debits 2.5% of its current balance; destination receives the identical amount. Reverse journals in **reverse edge order**. Reapplying the forward operation must regenerate the same source/target/amount journal and final digest.

Pinned origin `0vwxyz`, 8 sign paths × 3 H/O/N bands = 24 identities, 60 phase bins, optional shadow remains unresolved. Decimal values are normalized before hashing; this avoids false hash mismatches arising solely from trailing zero representations.

Run `python replay_v4.py`. Eight deterministic assertions check links, conservation, restoration, exact replay, positive receipts, link identities, 24 states, and phase wrap.

**Scope:** symbolic deterministic accounting only; no evidence of physical weak-force coupling, photon entanglement, or sub-Planck geometry.
