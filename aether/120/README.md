# AETHER-120 — Phase V integration and freeze

**Integration result:** PASS on 240 new synthetic cases (40 seeds × six delivery scenarios), 36 ticks each, **8,640 decisions** and **1,920/1,920** checks. Strict controller: **5,717 ACT**, **2,923 HOLD**, **0 unsafe authorization** in tested synthetic conditions.

The integration imports **AETHER-118's frozen selector and packet verifier**. Its source SHA-256 is `f7642313075830651348dd368496aa5f409236070466714b5010ab0fadc9ee4c`.

Test gates: replay equivalence, SHA-256 record chain, one decision/tick, current packet sequence for ACT, exact matching of admitted packet risk criteria, zero unsafe authorization in test cases, nonnegative bounded receipt accounting, and resume on the first permitted fresh safe audit after hazard.

Six scenarios: clean, delayed delivery, corrupted payload, acquisition counter rollback, outage recovery, mixed packet faults.

**Archive and provenance:** `inventory.csv` hashes eight *local executable snapshots*, including failed AETHER-117 and accepted AETHER-117B. These fingerprints are NOT asserted as byte-identical to every separately published GitHub file. Older bounds are inventoried, not exhaustively rerun. The previous failure and its corrected successor are both retained.

**Limitations:** synthetic evidence only. Trusted signer and counters, truthful independent measurement claims and authoritative clock state are assumptions. No independent assurance against a validly signed but false risk report or compromised issuer. Live Pages deployment remains unverified.

**Closure:** Phase V accepts eight bounded synthetic experiments, including corrections to failures; 8/8=100%. No Byzantine/quorum machinery added. New Phase VI starts independently at 0%.
