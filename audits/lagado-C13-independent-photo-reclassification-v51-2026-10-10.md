# Lagado Test051 — C13 Independent-Photograph Bond Reclassification
Date: 2026-10-10
PARENT: audits/lagado-original-closed-square-geometric-validation-v50-2026-10-10.md
STATUS: EXECUTED / SECOND SCAN DOES NOT REPRODUCE CLOSED LOOP UNDER SURROGATE / FROZEN SOURCE UNCHANGED

## The source model and photograph
- Source is an illustration of Jonathan Swift's fictional Academy of Lagado word machine, not a verified atomic or DNA diagram.
- Original 256 engraved source-grid addresses preserved; user-layer v41 ontology **200 ATOM / 54 OPERANT / 2 WITNESS** remains intact. The prior historical first-image graph has **109 model-selected similarity bonds**. Eleven newer candidate grid-neighbor links are separately recorded and never promoted or altered.
- Photograph supplied by user at Test035 covers only original rows A–E (80 grid positions, 56 source-model atom nodes) and not the lower rows needed for I15 and I8/K8/M8. Its SHA256 is eba02d6a92ec424d39e4815ef484be91af63a90d052325c207750ea22561aadf. Fixed manually sighted grid registration from v35 reused, with no target-image alignment optimization.
- All four C13-square source nodes C13,C14,D14,D13 are visible.

## Method — strict qualification
Exact v18 original model classification uses normalized `(X,Y,Z²)` geometry from v10 vectorized paths and a 20th-percentile all-208-atom squared-distance threshold.
The v51 implementation is **not an exact rerun** of that original feature extractor. It uses frozen v11/v32 image ruling subtraction and 41×41 normalized glyph *pixel skeleton* to approximate quadrant length, endpoints and junctions, computing a three-axis similarity feature in the same definitions. Source-only 208 nodes determine normalization and the 20th-percentile feature-distance² threshold, which is then frozen before evaluating the independent photograph. No source-model bonds, source codes, or photo labels were used to train/select an output threshold.
The reconstruction matches **all 208/208 first-image original four-by-four glyph codes**. Crucially, it reproduces only **321/382** original first-image bond-vs-nonbond decisions, and **77/93** of the original first-image decisions in the photographed A–E part. This baseline re-extraction disagreement must NOT be attributed to the new photograph.

## Exact C13 results
| Pair | Frozen original bond model | Reference image skeleton surrogate | Photograph skeleton surrogate (5px, 0 shift) | Photograph accepted across 20 settings |
|---|---|---|---|---:|
| C13-C14 | accepted | rejected | accepted | 18/20 |
| C13-D13 | accepted | accepted | rejected | 10/20 |
| C14-D14 | accepted | accepted | rejected | 3/20 |
| D13-D14 | accepted | rejected | rejected | 5/20 |
Total: original **4/4**, source-image surrogate **2/4**, second-photo surrogate **1/4**.
Predeclared crop-margin sensitivities 4,5,6,7 px × threshold shifts -10,-5,0,+5,+10 (20 total): C13 recovered 1–3 model bonds; **0/20 settings** yield full 4-bond closure. These are *classification decisions* under a surrogate from a digitized historical illustration, not chemical bond measurements.

## Broader visible control
Exactly **93** v22 neighbor pairs touch exclusively A–E available 56 original-model glyphs; 31/93 original accepted-model bonds; the baseline surrogate accepts 25/93; photo surrogate accepts 21/93. Exact old-vs-photo decision agreement 59/93; old-vs-baseline-surrogate 77/93. This again demonstrates measurable extraction and scan sensitivity; no statistical inference of a hidden code.
Earlier Test050 noted C13 shape hole-count agreement 4/4 but junction count 1/4 and mean binary-mask Dice 0.336685, consistent with unstable fine morphology. Images represent the SAME engraving in different photographs, not independent physical observations.

## Determinism and test outputs
- `build_v51.py`: frozen source/photo features, thresholds, all 93 visible edge audit, 20 sensitivity variants.
- `build_lab_v51.py`: standalone interactive offline HTML atlas with all 256 original source addresses, four C13 pair edges, switching between old model / baseline surrogate / independent-photo surrogate, twenty live sensitivity settings and embedded actual C13 two-photo comparison.
- `test_v51_browser.py`: **13/13 real Chromium Playwright interaction checks PASS**, no JS errors.
- `write_v51_docs.py`: human-readable method/limitations and ASCII C13.
- `package_v51.py`: 21-member complete deterministic ZIP with original engraving, user second photo, registered image, first-image tables and original frozen v41 roles. SHA256 **a02bfb11dd2f87a4f490638a9a8268e8aa7c3aa7538760ae88ccf1368dca44b1**. Full ZIP CRC and per-member SHA256 verified. Unpack the ZIP to a fresh directory, run the source builder, lab generator and browser tester: all success; generated CSV, JSON and HTML exactly byte-identical to original release.
- Further files `lagado_v51_C13_edge_decisions.csv`, `lagado_v51_20_conditions.csv`, `lagado_v51_visible_edges.csv`, `lagado_v51_summary.json`, `lagado_v51_report.md`, `lagado_full_ascii_v51.txt`.

## Decision
Retain old C13 four-edge model as a *first-image selected similarity square*. Mark full-loop second-scan replication **unconfirmed under cross-scan surrogate**, not disproven chemically, and do not merge the surrogate decisions into frozen 109 model bonds. Source comparison and photograph variability are measured separately; no demonstrated physical atomic or chemical meaning, DNA inheritance, source-encoded sexes or time physics.

NEXT: direct same-code `4x4` image similarity cross-scan across rows A–E with a new method fixed on source; ideally request an uncropped photograph showing F–P to evaluate I15 and all three lower candidate-completed squares, and repeat using exact v10 path extraction where possible.
