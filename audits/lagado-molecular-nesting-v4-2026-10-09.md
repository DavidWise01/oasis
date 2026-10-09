# Lagado candidate molecules — Gen0–Gen4 rotation/mirroring (2026-10-09)

STATUS::EXPLORATORY::SYMBOLIC_GEOMETRY_NOT_CHEMISTRY
SOURCE::256_CELL_LAGADO_ENGRAVING::IMAGE_DERIVED_16_BIT_GLYPHS
MODEL::{{1|1|2|4|8}}^{{n}}
INHERITS::audits/lagado-atomic-nesting-v3-2026-10-09.md

## Reproducible transformation
Each of 256 grid cells is a 4×4 binary occupancy image, divided into 8-bit logical core and 8-bit logical shell. A **candidate bond** is one of the 480 horizontal/vertical grid-adjacent pairs meeting both core agreement >=6/8 and shell agreement >=6/8.

Gen0=untransformed; Gen1=rotate each 4×4 glyph 90 degrees; Gen2=rotate 180; Gen3=rotate 270; Gen4=mirror each glyph horizontally. **Keep cell locations fixed**, and reparse bit fields after transformation. A persistent edge passes **all** five operations. A candidate molecule is a connected component of persistent edges, not a physical molecule.

## Direct results
- Gen0 edges: 64
- Gen1: 72
- Gen2: 64
- Gen3: 72
- Gen4: 64
- Persistent: 49 / 64 Gen0 edges (76.5625%)
- Persistent connected components >1 cell: 29
- Distinct geometric shape classes for nonsingleton groups after 2D rotation/reflection normalization: 6
- Largest persistent group: 10 cells, E5 E6 E7 F5 F6 G5 G6 H4 H5 H6.
- Persistent components by size (including singleton): 1:180, 2:21, 3:5, 4:1, 5:1, 10:1.

**Critical symmetry:** Gen0, Gen2 and Gen4 produce exactly the same bond graph for this rule; Gen1 and Gen3 also match each other. Five attempts are **only two effective orientation tests**, not independent evidence of five generations.

## Controls: 5,000 fixed-seed shuffles of each type
| Control | Mean persistent bonds | p(observed >= 49) | Mean largest stable group | p(largest >=10) |
|---|---:|---:|---:|---:|
| All symbols independently shuffled | 32.255 | 0.0014 | 4.706 | 0.0066 |
| Intact rows shuffled | 41.297 | 0.0166 | 6.676 | 0.05359 |
| Intact columns shuffled | 45.614 | 0.22795 | 6.522 | 0.06799 |
| Intact 4×4 regional blocks shuffled | 46.656 | 0.22156 | 10.699 | 0.71306 |

The original image-derived adjacency is stronger than all-symbol shuffling, but **not stronger than structural spatial nulls preserving columns/4×4 blocks**. Thus the interpretation is **local organization in a noisy engraving, not established alchemical translation, historical atomic encoding, or chemical bonds**.

## Audit controls and next steps
Results depend on a prior approximate raster threshold and the post-hoc 6/8 bond criterion. Re-extract from an independent source, perturb the threshold and registration, and compare against column/block-preserving controls before claiming cipher structure. Retain original images and model artifacts append-only.

OPERATOR::VOGEL_TESSY::PATRICIA_BOX::VECTOR_POINT
CYCLE::GEN0_TO_GEN4::APPEND_NEXT_CYCLE
WITNESS::GEOMETRIC_REPRODUCIBILITY::NOT_SEMANTIC_DECIPHERMENT
