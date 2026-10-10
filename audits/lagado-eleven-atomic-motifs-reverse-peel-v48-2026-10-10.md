# Test048 — LEELUU Reverse Atomic Distillation (11 -> 1)
Date: 2026-10-10
PARENT: audits/lagado-shared-positive-center-motif-v47-2026-10-10.md
STATUS: REVERSE PEEL PASS / EXTRACTED GLYPH GEOMETRY ONLY

## Scope & snapshot
Reverse-peel all eleven prior complexity-ranked engineering-selected adjacent pairs from the 16x16 Lagado engraving; first remove rank 11 least complex, lastly rank 1 most complex. Every one of the 256 source-addressed glyph cells remains at its original address. User-provided active symbolic partition frozen as 200 atom cells + 54 operants + witness P1/P16; 109 similarity-selected previously accepted source-derived MODEL BONDS left untouched. Eleven other adjacency pairs are explicitly engineered proposals, none intersects accepted 109. Their source features and ranked complexity came from Test046 and are not original historical chemical declarations.
Eight 25-atom v45 color classes and ee/uu/ll are model labels, not measured chemistry; symbolic sex labels on pair ranks female 6, male 7 are assignments, not biological evidence.

## Backwards rank sequence
Remove in descending rank number (from lowest to highest complexity):
11 A8-B8 (score 30)
10 I8-J8 (36)
9 I7-I8 (45)
8 M9-N9 (45)
7 L8-L9 (46), mnemonic male
6 K8-L8 (49), mnemonic female
5 I9-J9 (54)
4 C8-C9 (56)
3 J9-K9 (56)
2 M8-M9 (67)
1 M8-N8 (70)

At complete display the 11 proposed edges connect exactly 17 distinct glyphs in six acyclic candidate-only components, component sizes [4,3,3,3,2,2]. Since edges = vertices - components = 17 - 6 = 11, candidate-only cycle rank = 0.
Six components: A8--B8; C8--C9; I7--I8--J8; I9--J9--K9; K8--L8--L9; N8--M8--M9--N9. This is NOT one 17-atom molecule. Reverse peeling deletes proposed display edges only and does not delete the historical engraved glyphs or frozen original 109 model bonds.

## Key geometry contrast
- Candidate shared-center ranks 3+5: I9 Z.110 charge0 purple -> J9 Z.001 charge0 green -> K9 Z.111 charge0 orange. Along those two proposed links, topology Hamming distance = 3+2 = 5. Net dot charge = 0 throughout. **J9 has exactly one original accepted model neighbor, J8**. Both candidate links dormant in original v22 selected bond table.
- Candidate shared-center ranks female6+male7: K8 Z.111 charge0 green -> L8 P1.111 charge+1 orange -> L9 Z.110 charge0 green. Topology Hamming distance = 0+1=1, signed dot returns to zero across path. **L8 has two original accepted model neighbors, L7 and M8**. Both ranked candidate links dormant.
The different charge/topology profiles are reproducible assignments under the source image extraction but the previously available independently photographed second illustration only shows upper rows A-E, so these lower-row details have not been independently replicated. Historical reading as chemical bonds, male/female identities or coding is unsupported.

## Executed tests and files
- Pure-Python generator `build_lagado_v48_reverse.py` checks 256/200/54/2, 8*25 labels, 109 accepted graph bonds, 11 disjoint candidate edges, source token match, exact 17 vertices/6 components/0 cycles, J9 and L8 center profiles, 12-stages reverse-peel counts.
- Offline source-coordinate SVG viewer `lagado_v48_reverse_distillation_lab.html`: actual A-P / 1-16 256-cell atlas, 109 accepted edges, rank 11->1 reversible overlay, clickable source atom inspector, 11 scores, six components and paired-center comparison.
- Real Chromium Playwright `test_lagado_v48_browser.py`: **16/16 PASS**: all 256 cell targets, 109 accepted edges unchanged, 11 proposal edges, reverse/undo/restore, counts 17 and 6, J9/K8 inspection, zero JavaScript errors. Browser run used system /usr/bin/chromium and page.set_content.
- 16-member deterministic reproducible ZIP `lagado_v48_reverse_distillation_bundle.zip`, SHA256 `1af2c5b0f318fee290b673aad1f57c8b2c09ad13a17349306f6f1c470672bfe2`, twice byte-identical, CRC and each SHA256 file digest pass. Contains frozen source CSVs, script, browser tests, all eleven reverse ranks, 12-step peel log, five degree-2 center comparisons, 17 source atoms, ASCII v48, report and offline viewer.
- Original source captures and previous v41-v47 releases are not modified. No previously retired annotation appears in newly derived text assets.

NEXT ATOMIC TARGET: continue strict source-shape comparison of the remaining reverse-peel sequence or independently photograph complete lower-row glyphs before mapping ee/uu/ll to empirical chemical states. **No routing optimization is needed.**
