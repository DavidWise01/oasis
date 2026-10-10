# Lagado / LEELUU Test052 — Direct Frozen 16-Symbol Glyph Cross-Scan Reproduction
Date: 2026-10-10
Parent: audits/lagado-C13-independent-photo-reclassification-v51-2026-10-10.md
STATUS: EXECUTED / 19-OF-19 REAL CHROMIUM CHECKS / REPRODUCIBLE / NO CHEMICAL DECIPHERMENT

## Commit intent
User instructed COMMIT, NEXT. Test051 was already committed as c4bfa070afe3f9f9d1558b0c2e6dc63c982f12e1. This Test052 is the append-only next study. No earlier v22/v41/v51 source or model bond was modified.

## Frozen records / scope
Original 16×16 Lagado engraving in Swift's *Gulliver's Travels*. Source role ledger 256 = 200 ATOM + 54 OPERANT + 2 P1/P16 WITNESS; 109 frozen first-image similarity-selected model bonds (not observed chemical bonds); 11 separate proposed dormant original-grid neighboring-glyph pairs from v46. Old source v22 has 208 atom candidates, and source-derived 4×4 glyph code extraction from Test051 reproduces all 208 frozen v22 16-symbol codes. Source image SHA256 bea5f699b53f9306f37708fc81edbd9491ecaf042cd3971c32497c376e0ae21f. The already registered second photograph depicts the SAME engraving, cropped to original rows A-E, 56 current original-model ATOM-role cells. No lower rows F-P are independently visible.

## Protocol predeclared from Test051
Use unchanged Test051 local image binarization/ruling subtraction, skeleton normalization to 41×41, 4×4 area resize, bit threshold >3 (16 '.'/'|' pixel-feature positions). Crop margin 5 px, intensity threshold shift 0 for primary experiment. Compare same engraved source address in first-image frozen v22 code and reconstructed second image; loss = number of differing 16 code bits, i.e. Hamming distance. Calibration on no genetics or chemical evidence. Twenty margin/threshold sensitivity settings fixed in Test051 remain 4,5,6,7px x -10,-5,0,+5,+10 shifts.

## 56-atom cross-scan findings
- Exact identical 16-symbol code at same address: **1/56**.
- Source-position mean Hamming mismatches: **5.3392857143/16**.
- 20,000 deterministic independent Monte Carlo shuffles permuting SECOND-image codes ONLY WITHIN the corresponding original printed A-E source row, preserving row sizes and code marginals, seed 520052: mean shuffled Hamming **6.5104517857/16**.
- Difference in mean mismatches **1.1711660714 bits/16** in favor of real original positions; conditional one-sided Monte Carlo p=(1+0)/(20000+1)=**0.0000499975**.
- Row-cluster 10,000-bootstrap percentile CI for this within-row correspondence advantage: **0.781159 to 1.445469** fewer bit differences. Only five independent row blocks and post-selected registration/extractor; this is exploratory and only describes evidence of same-position pattern correspondence.
- Exact-code agreement stays only 1-3 /56 under all twenty preregistered Test051 image extraction settings. Overall mean Hamming 4.892857–5.732143.
- C13 square second-scan difference counts: C13 **11**, C14 **3**, D13 **6**, D14 **7** bits/16; all four C13 glyphs exact in **0/20** variants.
- The four original C13 edges remain the original model-selected similarity bonds; cross-scan v51 reconstructed surrogate selected 1/4, and this v52 study does not replace that classifier with Hamming.
- Across 93 original source-grid-adjacent atom pairs visible in both images, Spearman rank correlation of pairwise code Hamming distance across photographs is only **rho=0.047347, nominal p=0.6522**. Source-glyph address identity is partly replicated but the Hamming ordering of adjacent glyphs is not.
- Only TWO of eleven proposed dormant neighbor pairs both appear in photo: candidate rank4 **C8-C9**, first-photo code Hamming 6 and second-photo 7; candidate rank11 **A8-B8**, first and second photo distances both 7. The other nine cannot be tested from cropped photograph. Neither is promoted to a source-model bond.

## Evidence decision
Better code agreement at the correct engraved address than random within-row address shuffle is a fair within-illustration replication finding. It does **not** demonstrate codons, nuclear chemistry, electron charge, actual atoms, inherited ancestry or any source-encoded male/female roles. The photo is not an independent scientific sample. Permutation p is conditional on fixed crop/feature choices after many earlier exploratory analyses.

## Artifacts and deterministic release
Complete local bundle `lagado_v52_glyph_code_bundle.zip`, SHA256 **704e3c4b90f517126b2f9d71dbb4cbc7c347b14e2f187cfa8b21e82a3d8a339f**, 22 files incl. source reference picture, registered photograph, untouched original frozen v22 nodes and edges, v41 ledger, v46 rank candidate file, executable `build_v52.py`, `build_lab_v52.py`, `package_v52.py`, `test_v52_browser.py`, 56 exact source/photo code rows, five row-wise controls, C13 and 11 candidates, 93 adjacency edge comparison, 20 sensitivity variants, results JSON, ASCII v52, report, offline lab and real Chromium image preview. ZIP member SHA256 and CRC pass; two consecutive ZIP builds identical SHA256.
Fresh-directory clean-room unzip + run build_v52.py + build_lab_v52.py produces byte-identical JSON/CSV/report/HTML sample outputs.
Standalone interactive offline lab `lagado_v52_code_comparison_lab.html` has all 256 clickable source addresses, 56 photographed glyphs, side-by-side 4×4 first-photo/second-photo/mismatch blocks, available two candidate pairs, C13 actual compared photo crop, five-row controls and 20 settings. Real /usr/bin/chromium Playwright 19/19 PASS including unphotographed lower-row reporting and zero browser script errors.
No retired legacy wrapper was used in newly derived content. Source image and prior frozen model inputs unchanged.

DECISION::IMAGE-ADDRESS-CORRESPONDENCE_REPRODUCED::EXACT_CODES_NOT_STABLE::NEIGHBOR_DISTANCE_ORDER_NOT_REPRODUCED::NO_CHEMICAL_SOURCE_EVIDENCE
NEXT::FULL_SECOND_IMAGE_ROWS_F_TO_P_FOR_I15_K8_L8_M8_LOOPS; OR PREDECLARED REGISTERED_IMAGE_REFINEMENT WITH TRUE HOLDOUT TO TEST STABILITY, WITHOUT CHANGING THE 109-EDGE EVIDENCE RECORD.
