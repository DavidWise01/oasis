# Lagado Cipher — Test 008: independent topological 3-register (2026-10-09)

STATUS::EXECUTED_SYMBOLIC_SIMULATION::NO_DECIPHERMENT
LINEAGE::audits/lagado-nested-9631-v7-2026-10-09.md
SOURCE::lagado_atomic_v3_atoms.csv
SOURCE_SHA256::8dc7f3cfaae7c8c9a958e7aae80d58e7783d1e06602b55a10e8600c8da8bf2ea
EVENTS::lagado_molecular_reactions_v5_ledger.json
EVENTS_SHA256::e07f57848dcd24f336d34e1864ca5f7c489b44c772160d75e4451d0a89963cb0
MODEL::{{n}}^{{n}}::9/6/3/1

## Fixed controls and changed component
Keep 256 v3 image-derived 16-bit glyphs, 53 v5 Gen4 shell swaps, adjacent-site grid edges (480), 9-position 3×3 overlapping-window ternary transform, six signed row/column reductions, old final polarity root, and progressively thresholded core/shell gates. Change **only the 3-position gate** (prior v7 gate derived directly from the nine-state center column and rejected zero bonds).

Replace the 3-register with direct topological features computed from the **original 4×4 occupied-pixel graph**:
- position 1 (H): any 4-connected occupied path from left boundary to right.
- position 0 (C): whether there is an occupied-pixel adjacency **graph cycle** (0 means acyclic).
- position 1 (V): any 4-connected occupied path from top boundary to bottom.
The literal `101` is a template, not an assertion about all atoms. A pair passes if at least 2/3 of these features agree. Other thresholds unchanged. This is exploratory model selection after viewing an engraving, not independently verified alchemy or historical decoding.

## Outcomes
| Stage | v7 bonds | v8 bonds | Largest v8 group |
|---|---:|---:|---:|
| Gen4 baseline | 129 | 129 | 22 |
| 9 | 63 | 63 | 5 |
| 6 | 59 | 59 | 5 |
| independent 3 | 59 | 56 | 5 |
| final 1 | 50 | 47 | 5 |

145/256 atom triad labels changed relative to v7. New three gate rejected 3 specific pairs: D14–D15 (`100` against `011`), J12–K12 (`011` against `110`), J14–K14 (`100` against `111`). The new 3-position register is **no longer redundant** on the observed 59 bonds surviving the 6 gate.

All 256 final glyphs passed the 4 rotations × 3 symmetry observations (original, left-right reflection, top-bottom reflection): H/V swap on odd quarter rotations while cycle indicator is invariant. The source 16-bit values and prior event lineage were not changed. Gen0 original bonds remain 64; core occupancy 1166, shell 1024, total 2190.

## Spatial controls: 4000 permutations each, identical pipeline
| Permutation | Mean final bonds | p(final>=47) | Mean bonds excluded at 3 gate |
|---|---:|---:|---:|
| all sites freely shuffled | 18.142 | 0.000250 | 1.341 |
| whole rows shuffled | 35.292 | 0.000250 | 1.778 |
| whole columns shuffled | 34.242 | 0.002000 | 3.025 |
| intact 4×4 blocks shuffled | 45.078 | 0.190202 | 3.148 |

The observed final 47 is **not exceptional** under the intact-block preservation null (p≈0.19). Three exclusions demonstrate *new computational discrimination* under the chosen gate, **not cipher interpretation or chemical mechanism**.

## Provenance and limitations
All derived outputs are exploratory: sources were approximately rasterized from one historical image; gate thresholds are post-hoc. No independently sourced 1726 text, key, alchemical instruction, chemical bond or decoding was discovered. Run preregistered algorithm on independent clean engraving scan and evaluate block-aware controls. Offline bundle `lagado_9631_v8_bundle.zip` packages executable Python, two source inputs, derived per-atom and per-edge CSVs, JSON statistics, full report, and interactive local HTML. Browser JS syntax passes Node `--check`, but automated Chromium render validation was inconclusive in this environment.

NEXT::REPLICATION_ON_INDEPENDENT_SCAN_AND_CROP_THRESHOLD_SWEEPS
