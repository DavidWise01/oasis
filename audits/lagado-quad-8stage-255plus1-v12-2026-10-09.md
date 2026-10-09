# Lagado Test 012 — Full 255 + 1 eight-stage Quad/Vector/Voxel/Vogel kernel
DATE::2026-10-09
STATUS::ENGINEERING_PASS::CIPHER_UNDECODED
REPOSITORY::DavidWise01/oasis
PARENT::audits/lagado-atom-foundry-v11-2026-10-09.md
SOURCE_SHA256::bea5f699b53f9306f37708fc81edbd9491ecaf042cd3971c32497c376e0ae21f

## Exact interpretation of 255 + 1
256 **historical-image-derived source grid cells**, numbered A1–P16 row-major. First 255 source entries form the run; P16 is the last source glyph and seals the hash-chain witness. Not 255 arbitrary atoms plus an invented atom or a new historically evidenced symbol. All 256 undergo all eight stages.

## Stage model — user's canonical order
REGISTRY::1|1|2|4|8::16_TOTAL_LOCAL_POSITIONS
VOXEL::2^3::8_LOGICAL_BIT_ADDRESSES
1 DIMENSION: normalized 2D image and virtual z=0/1 feature channels
2 QUAD: analytically clip traced 41×41 pixel glyph vectors into A(top-left), B(top-right), C(bottom-left), D(bottom-right), with midline length/anchor mass split exactly
3 VECTOR: vector-chain endpoints, path-segment count, total Euclidean lengths and local cos(2θ),sin(2θ) direction moments
4 VOXEL: lower four bits = occupied strokes in quads; upper four bits = path endpoint occupancy per quad; this is a *defined* logical voxel, not measured 3D matter
5 VOGEL: canonicalized full 8-element D4 symmetry orbit (rotations R0,R90,R180,R270 × mirror), based on quantized quad length, endpoints, voxel pattern
6 OPERANTS: source identity plus spatial-neighbor objects (2–4 per source)
7 OPERATORS: validate R90 followed by inverse R270, mirror followed by mirror, and length preservation
8 FINAL: append-only per-cell state with SHA256(prev|content) and fixed Gen0 anchor / P16 tip

## Actual benchmark
- Source glyphs processed: **256/256**.
- Stage checks: **2048/2048**, 256/256 at all eight independently named stages.
- Straightened path segments: **3102** (source reduction inherited from Test010/011).
- Distinct 16-bit v11 codes: **238**.
- Canonical vector Vogel signatures with very fine quantization: **256** distinct; this is *too fine* for noise robustness, not evidence of 256 chemical elements.
- Orientation/mirror D4 equivalence: **2048/2048**; mathematical consequence of group canonization, not independent interpretation.
- 480 spatial-neighbor candidate edges. Joint threshold quad normalized-vector cosine ≥0.90 and logical voxel agreement ≥6/8: **170 candidate bonds**.
- Exact return of original points by inverse rotation/mirroring: 256/256 source atoms pass.
- Chain verifies with pinned Gen0 anchor and P16 tip; changing any one of 256 source 16-bit codes fails verification: **256/256 altered-event detection**. Requires trusted outside anchor/tip.

## 2,000 equal-pipeline geometric shuffle controls (Monte Carlo plus-one p)
| Shuffle | Mean candidate bonds | P(null≥170) |
|---|---:|---:|
| All atoms freely shuffled | 123.079 | 0.00050 |
| Intact rows shuffled | 139.979 | 0.00050 |
| Intact columns shuffled | 166.065 | **0.28186** |
| Intact 4×4 blocks shuffled | 160.356 | 0.01449 |

Not better than column-preserving null. Block control is smaller but because thresholds are exploratory on the same original image, and several controls were examined, do **not** promote it to ciphertext evidence.

## 27 actual image micro-perturbations
Cycle crop dx/dy in [-1,0,+1] pixels and grayscale threshold Δ in [-4,0,+4]. 26 exclude exact baseline, statistics are medians from **256** glyphs:
| Metric | Median surviving glyphs |
|---|---:|
| Exact 16-bit old bitmap | 74 |
| Similar quad vector profile cosine ≥0.95 | **199** |
| Exact 2×2×2 stroke/endpoints voxel register | **213** |
| Exact fine-vector D4 canonical fingerprint | **5** |

All 256 sites retain some extracted vector geometry under each setting. Across every one of the 27 settings, **74** sites always reach quad cosine≥0.95 and **147** preserve exact voxel occupancy. This demonstrates improved coarse image representation, but an unstable high-precision label.

## Anchors
GEN0_ANCHOR_SHA256::ab9feaa62154fffee364bbb415c751bb3c322f0f7529282f4311f84f8bc33b29
P16_WITNESS_TIP_SHA256::9bda028b04b84f512f4a992c5299dc06517c0a524e9ef0003169d1e507cdb298

## Reproducibility and UI
Locally generated self-contained files:
`lagado_quad_8stage_v12_lab.html`
`lagado_quad_8stage_v12_bundle.zip`
`lagado_quad_8stage_v12_atoms.csv`
`lagado_quad_8stage_v12_edges.csv`
`lagado_quad_8stage_v12_micro.csv`
`lagado_quad_8stage_v12_report.md`
`build_lagado_quad_8stage_v12.py`
`build_lagado_quad_8stage_v12_ui.py`

Chromium Playwright `page.set_content` rendered the self-contained lab without errors: select A1 and P16, R90 and mirror, 27-run stress table, hash anchor/tip, all seven JS in-page validation assertions true. `node --check` passes and `zipfile.testzip()` returns None. The browser preview is `lagado_quad_8stage_v12_preview.png`.

## Limits
All 256 objects are algorithmic symbols derived from an imperfect 2D engraving; no proven plaintext, historical alchemical key, material atom, physical Planck-depth effect, or independent-image replication. Next target: coarser, threshold-robust Vogel family key, preregistered and tested against second engraving and column/block controls.
