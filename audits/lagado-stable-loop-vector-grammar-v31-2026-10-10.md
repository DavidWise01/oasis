# Lagado Test031 — Seven Stable Ink Loops and Centered Vector Grammar
Date: 2026-10-10
State: EXECUTED / REPRODUCIBLE / INSUFFICIENT INDEPENDENT EVIDENCE FOR CIPHER GRAMMAR
Parent: audits/lagado-original-ink-contours-v30-2026-10-10.md

## Frozen inputs, exclusions and protocol
- One preserved Lagado raster source, 256 cells (208 active, 48 reserve); earlier source indexing and P16 witness unchanged.
- 208 frozen source glyphs, 382 grid adjacencies, 109 previous **model-defined** graph bonds; no original bonds or node labels changed.
- The legacy EE wrapper is excluded from all Test031-derived text outputs; original image and previous historical audit files are preserved, not destructively modified.
- Stable-loop center means at least one ink-defined enclosed hole retained under all 20 earlier crop-margin and grayscale-threshold extraction variants. These variants use ONE scan, not 20 independent editions. Exactly seven: I6, I15, K11, M5, N5, O10, P7.
- Pin each measured stable-loop glyph as a symbolic 0/3D center, inspect graph neighbors and direction ports; do not infer biological neural chemistry or literal 4D time.

## Seven-center atlas
|Center|Frozen v22 token|Graph degree|Original bond port class|Candidate skeleton junctions|At least one original graph cycle|
|---|---|---:|---|---:|---|
|I6|Z.000|2|straight north/south|1|no|
|I15|Z.110|2|corner east/south|3|yes|
|K11|Z.111|2|corner north/east|4|no|
|M5|Z.111|0|isolated|2|no|
|N5|Z.110|0|isolated|2|no|
|O10|P1.111|1|endpoint east (O11)|4|no|
|P7|Z.000|1|endpoint north (O7)|3|no|

The three center-anchored two-edge paths are H6–I6–J6 (straight), I16–I15–J15 (corner), and J11–K11–K12 (corner). The two corners are congruent under right-angle rotation/mirror, but not evidence of semantic code. I15 is on pre-existing 4-cycle I15-I16-J16-J15-I15. M5 and N5 are **grid adjacent but have zero accepted bonds**. A loop in the recovered ink of a single glyph is distinct from a cycle in the derived macro bond graph.

## Six metrics and 20,000 geographic nulls
Freeze all 208 nodes, source labels, bonds, and image coordinates. Reassign seven loop-center labels by independent without-replacement shuffles **within the original 4×4 source tiles**, maintaining the exact observed 7-loop quota in each tile. Pre-specified counts measured in each null:
|Measure|Observed|Null mean|One-sided p(null ≥ observed)|6-test Bonferroni corrected p|
|---|---:|---:|---:|---:|
|centers with degree ≥2|3|2.0908|0.345983|1|
|two-edge centered wedges|3|2.6216|0.460927|1|
|centers with extracted junctions|7|4.30055|0.024049|0.144293|
|grid-adjacent pairs of stable loops|1|0.78745|0.60352|1|
|accepted-bond connected stable-loop pairs|0|0.1632|1|1|
|centers located on an original graph cycle|1|0.26495|0.264987|1|

Junction co-occurrence (7/7) is **exploratory only**: six measured features were compared, and hole/junction extraction uses the same pixels and topology, so not an independent biological or historical fact. No tested metric survives conservative six-way multiplicity. Prior Test030 found ZERO components with two enclosed holes, hence no full figure-eight loop recoveries.

## Verification and deliverables
- Reproducible Python runner `build_lagado_loop_grammar_v31.py` uses pre-existing V22 and V30 datasets, independently checks 208/382/109/7/3, enumerates the 4 local-role classes (isolated×2, endpoint×2, corner×2, straight×1), and executes seeded 20,000 null trials.
- Self-contained interactive `lagado_loop_grammar_v31_lab.html` includes original source raster, 208-node bond graph, 7 original crops and masks, pinned glyph-selection, row/column identification, 17/52/104/208 capacities, original edges vs accepted bonds, six-feature significance table.
- Chromium Playwright `set_content` 13/13 checks PASS; selection I15/I6/M5, capacity 52 exactly, bond visibility, raw raster toggling, six controls, and zero JS runtime errors. Node --check PASS. Browser screenshot available.
- Complete 18-file standalone source+data+HTML+test ZIP; CRC PASS, SHA256 **4ffdc3c091b4b42bb6d57d8094864651e1ead5a78001980474c5ce89eaaf3e69**. All its text entries checked absent legacy EE wrapper.
- Local files: `lagado_loop_grammar_v31_bundle.zip`, `lagado_loop_grammar_v31_lab.html`, `lagado_loop_grammar_v31_report.md`, `lagado_loop_grammar_v31_nodes.csv`, `lagado_loop_grammar_v31_wedges.csv`, `lagado_loop_grammar_v31_null_trials.csv`, and PNG preview.

## Interpretation and next target
Stable ink holes provide a useful local provenance feature and four descriptive graph roles. No robust recurring center grammar or causal time/codon identity has been demonstrated. The stronger next test is *independent second high-quality print*: freeze the same extraction recipe, register the glyph source cells, and determine whether stable ink holes and vector-port pairings replicate without retuning thresholds.
