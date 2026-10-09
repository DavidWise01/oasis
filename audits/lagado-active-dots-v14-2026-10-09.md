# Lagado Test 014 — Active Two-Dot Inference / 255+P16
Date: 2026-10-09
STATUS: COMPUTATIONAL PASS; NO HISTORICAL DECIPHERMENT
PARENT: audits/lagado-redot-1128dotdot-v13-2026-10-09.md

## Canon
`2^3 :: 1+1+2+(dot_minus+dot_plus)+8=16`
`dot_minus+dot_plus=4`
SOURCE_COUNT::255+P16=256
SOURCE_IMMUTABLE::TEST012+TEST013
REALIZATION::GEN0 -> PROPOSE -> QUAD_VECTOR_NEIGHBOR_FEEDBACK -> FINAL_WITNESS

## Implementation
Dots are complementary latent inference operators. Each source is given five candidate allocations k∈{0,1,2,3,4} for dot-minus, with dot-plus=4−k. The unary score for k is −(r−k)^2/(2σ²), where r=4(A+D)/(A+B+C+D) for vector quadrants A–D, σ=0.46. An edge is a v12 4-neighbor atom pair with cosine of normalized quad lengths ≥0.90 and voxel agreement ≥6/8. Four synchronous message-passing rounds add β=1.20 times mean adjacent posterior mass of the D4-invariant unordered family min(k,4−k). Low-confidence candidates are marked if difference between first and second most probable k <0.15. All of these thresholds are **proposed** modeling decisions, NOT recovered historical key parameters.

## Results
- 256/256 conservation checks and append-only source links pass; P16 remains final original source.
- 170 v12 reference vector+voxel edges.
- Dot compatible bonds: 98 hard v13 → 134 active v14 (+36 by a *directly rewarded* metric).
- 23/256 changed inferred source dot families; 24/256 flagged low-confidence.
- All 256 source identities retained; 256/256 single-record ledger mutations detected relative to external pinned anchor/tip.
- Whole-grid D4 rotation/mirror applied to all glyphs, 8 variants ×256 = 2048 family comparisons; no changes to dot family assignment or 480 neighbor bond decisions for all variants. Group-equivariance is an invariant of this design, not proof of historical semantic truth.

## Real image micro robustness
Rerun image extraction independently on all 27 combinations of crop shifts (−1,0,+1) px along x/y and local ink threshold offsets (−4,0,+4) grayscale units; recompute both bond graph and dot posteriors from each altered scan, without using baseline decisions. Across 26 altered runs:
- Median same dot families (hard/active): 194.5 / 196 out of 256.
- Median retained original bonds (hard/active): 52 / 77.5 (different original bond totals 98 / 134, so do not interpret as direct matched fraction).
- Dot families unchanged in ALL 27 runs: hard 69 / active 63. Increased median recognition but worse stringent all-run stability: no universal improvement established.

## Same-optimizer nulls: 700 independently permuted layouts each
| Reordering | Hard mean | Active mean | p(active ≥134) | Null average active-minus-hard gain | p(gain ≥36) |
|---|---:|---:|---:|---:|---:|
| Free shuffle | 77.550 | 98.439 | .001427 | 20.889 | .004280 |
| Row shuffle | 82.296 | 106.439 | .001427 | 24.143 | .001427 |
| Column shuffle | 101.467 | 134.541 | .557775 | 33.074 | .292439 |
| Intact 4x4 blocks | 94.141 | 127.914 | .054208 | 33.773 | .216833 |

**Verdict: computationally functioning complementary operator, not convincing cipher evidence.** The gain in bonds is deliberately rewarded in the objective. Spatially structured column-preserving controls behave similarly. Block-control active-bond p≈.054 is not confirmation, especially given post-hoc exploratory model design. No decoded message, historical alchemical key, physical atomic interpretation or 10^-36m resolution is supported by this dataset.

## Artifacts
Generated locally and ZIP CRC checked: `lagado_active_dots_v14_bundle.zip`, SHA256 `5bd359faf45f327fbc557557480066b0419034fbfb3b310c3919fa16cb2540f6`.
Contents: full Python original and UI builders, v12/v13 input data, source image, independently generated CSVs, stats, event hashes, report, standalone interactive HTML, preview, test scripts, code and manifest.
Browser: Chromium successfully rendered stand-alone HTML and passed 256 tile count, 134 bonds at β1.2, 98 at β0, 23 family changes, 24 ambiguous, P16 selection, changed-filter count, no page JS errors. CSS/browser artifact backed by screenshot.

## Next falsification
Freeze model coefficients and extraction pipeline and run on a separate, independently acquired image of the engraving, with the same column- and 4×4-block-preserving controls. No promotion to verified decoding before that replication.
