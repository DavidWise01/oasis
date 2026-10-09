# Lagado Test 013 — Re-dot correction / 255+1 benchmark
DATE::2026-10-09
STATUS::256_OF_256_PASS::ENGINEERING_ONLY::NO_HISTORICAL_DECIPHERMENT
PARENT::audits/lagado-quad-8stage-255plus1-v12-2026-10-09.md
PRIMITIVE::2^3::11248::1128..=4=16
CORRECTED::1 + 1 + 2 + (dot_minus + dot_plus) + 8 = 16
INVARIANT::dot_minus + dot_plus = 4
RECORDS::255 + P16(256th) = 256 sources, no 257th source generated

## Structural correction
Preserve the original 4 geometric quads as **evidence**, but do not commit them to four one-bit semantic registers. The two dots are initially unresolved symbolic capacity slots totaling 4; at the vector observation stage infer an ordered pair (0,4), (1,3), (2,2), (3,1), or (4,0). Proposed measurement: `r=4*(quad_A + quad_D)/total_vector_stroke_length`, `dot_minus=round(r)`, `dot_plus=4-dot_minus`. D4 planar rotation/reflection can exchange diagonal roles; unordered dot family should be invariant. The continuous value and near-threshold alternative pair(s) are preserved, not overwritten. This is a **declared experimental mapping**, not a recovered 1726 decryption key or physical particle model.

## Actual results
- Source records: 256/256, original Test012 eight stages unchanged: 2048/2048.
- Re-dot capacity checks: 256/256, sum 4 and total 16.
- 2048/2048 D4 transforms produce the same unordered dot family.
- Distribution ordered: 0:4→2, 1:3→53, 2:2→146, 3:1→50, 4:0→5.
- D4-unordered families: 0:4→7, 1:3→103, 2:2→146. This is deliberately coarse — only 3 derived families, and collapses information.
- 52/256 raw inferences fall near a predeclared 0.10-unit rounding cutoff; preserve alternate assignments.
- Original Test012 quad/vector/voxel candidate bonds 170/480; after adding exact unordered dot-family compatibility: 98/480.
- 256 single-record modifications rejected by sequential SHA-256 history relative to externally retained Gen0/P16 digests.

## Real image stress: 27 crop/ink variants
Micro variants use source image tile-offset dx/dy∈{-1,0,1}px and grayscale changes ∈{-4,0,4}; median excludes unchanged baseline.
- old exact 16-bit bitmap: 74/256 matching
- ordered dot pair: 194/256
- unordered D4 dot family: 194.5/256
- uncertainty-aware overlap of candidate splits: 225/256
- 69/256 unordered dot family labels unchanged across **all 27** variants.
This improvement is expected from heavy category compression and cannot itself prove recovering underlying historical information.

## Spatial controls; 1,200 equally tested permutations
| Shuffled layout | Expected redot-compatible bonds | One-sided p(≥98) |
|---|---:|---:|
| Free symbol shuffle | 77.447 | 0.005828 |
| Whole rows | 82.677 | 0.002498 |
| Whole columns | 101.477 | 0.829309 |
| Intact 4x4 blocks | 93.974 | 0.146545 |

**The measured 98 are NOT exceptional versus intact columns or 4×4-block shuffle**. This remains a geometric processing hypothesis, not evidence of an ancient atom cipher, alchemical secrecy, or actual molecular physics.

## Reproducibility
Local generated `lagado_redot_v13_bundle.zip` includes Python source code, original v12 builder, original source image, v12 JSON inputs, v13 complete data, per-atom and per-bond CSV, 27-variant results, full report, Chromium test script, tested interactive self-contained HTML and preview PNG. ZIP integrity verified; `node --check` script passed. Chromium Playwright system installation rendered the viewer with zero page errors: 256 tile controls, A1 selected, P16 checked, rotated 90 degrees (3+1→1+3) and mirrored; all seven in-page validation assertions PASS.
ZIP_SHA256::df4285f5a1b85f942faaeb1571643f37f69cd9ff48ac56b700a8e8f45c8b0f18
HTML_SHA256::3e35ee2bb2acf9a85e5744cd305e27eb79c6b9e6ff0dd1eb314699ae77e5e666
REPORT_SHA256::3dc2d09a0deaf0d8db39de72dbf28878802bd31d1144f4165040306fc6e502bd

NEXT::repeat on genuinely independent high-quality engraving with frozen operator extraction; test alternative dot allocation functions without training on the test image.
