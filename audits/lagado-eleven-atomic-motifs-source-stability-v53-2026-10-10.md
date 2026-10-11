# Lagado / LEELUU Test 053 — Eleven Motif Single-Scan Robustness
Date: 2026-10-10 (user-local)
Parent: audits/lagado-glyph-code-independent-photograph-v52-2026-10-10.md
STATUS: EXECUTED / 16 OF 16 CHROMIUM TESTS / CLEAN-ROOM EXACT REBUILD / CHEMISTRY UNPROVEN

## Frozen historical source/model boundary
- Swift's *Gulliver's Travels* Lagado writing-machine engraving is a fictional illustration, not a physical-chemistry or DNA measurement.
- All **256 original positions** remain unchanged, partitioned into **200 atom-role glyphs + 54 operants + 2 witnesses (P1/P16)**.
- **109** previously selected glyph similarity MODEL bonds remain frozen. All **11** rank-ordered candidate original-grid neighbor pairs remain individually labeled as engineered proposals, not accepted source bonds or real atomic chemical links. Eleven candidates use 17 distinct glyph positions.
- Symbolic eight-color, ee/uu/ll, C.A.R.B.O.N., rank6 female/rank7 male and 8^8^5^3^1 classifications not independently identified in the engraving; earlier user-assigned categories retained without asserting actual chemistry.

## Test design
Using the first 788×784 original scan and its exact previously frozen v52 skeleton-normalized 4×4 binary code extractor, apply **20 parameter settings**: margin 4/5/6/7 pixels × threshold shift -10,-5,0,+5,+10. Each re-extracts glyph codes from the SAME source scan. One setting (margin 5, shift 0) is the original baseline, so that exact match is **by construction** and not evidence of replication. v22 first-image frozen original 16-bit codes are exactly recoverable for all **208** old atlas nodes, as another deterministic reproduction check.
For each current 200 atom glyphs, compute Hamming changes against its original 16-bit code. For each of 11 candidates, compute changes in the pair's inter-glyph Hamming distance. This latter comparison can be stable even when the two endpoint glyphs individually change. No attempt is made to rerun v22's original stroke-segment/path extractor, so these perturbations do NOT validate or rerank its high-level complexity score or frozen signed-charge/topology tokens.

## Measured results
- Overall 200-atom average code changes = **2.38225/16** across all twenty settings; **4.71/20** mean exact-code setting count per atom (includes baseline).
- Eleven candidate source-neighbor pairs, mean absolute change in inter-glyph Hamming distance = **1.404545** across conditions.
- All **256** dormant atom/atom grid neighbors in the 200-atom role classification, same metric = **1.574414**.
- 20,000 seeded random subsets of 11 from those 256 candidate neighbor positions, without replacement, produce exploratory one-sided **p=0.20784** for candidates being more stable. No persuasive enrichment.
- Spearman rho between eleven frozen stroke-complexity scores and mean pair-code instability ≈ **0.0507** (tiny and descriptive).
- Of three preselected anchor structures:
  1. M8,N8,M9,N9: **2.075 mean differing bits per atom** across conditions;
  2. K8,L8,L9 (user mnemonic female rank6 / male rank7): **3.100**;
  3. I9,J9,K9 (neutral center): **3.1833**.
  All three have exactly one of the twenty settings where ALL the selected member glyphs match baseline codes; that is the original baseline setting and is **not independent reproducibility**.
- On pairwise *distance* stability (not per-atom stability), among all eleven the smallest average change is **K8-L8 rank6 = 0.80**; other rank examples M8-N8 rank1 = 1.20, M8-M9 rank2 = 2.15.
- Available user-supplied second photograph covers original A–E only, thus neither M/N nor K/L nor I/J shared lower-row motifs is independently photographed. Only A8-B8 and C8-C9 among eleven have full visibility in this second scan; cross-photograph code sensitivity was studied separately in Test052.

## Exact sequence / frozen original-position rank scores
1 M8-N8 70 (pair-distance change 1.20)
2 M8-M9 67 (2.15)
3 J9-K9 56 (1.20)
4 C8-C9 56 (1.20)
5 I9-J9 54 (1.60)
6 K8-L8 49 (0.80; user female mnemonic)
7 L8-L9 46 (1.85; user male mnemonic)
8 M9-N9 45 (1.00)
9 I7-I8 45 (1.10)
10 I8-J8 36 (2.00)
11 A8-B8 30 (1.35)

## Interactive reproducibility / release
- Offline `lagado_v53_motif_stability_lab.html` presents 256 original-source positions, 109 accepted-model bonds solid vs 11 proposed adjacent-cell pairs dashed, selectable 11 rank records, separate color/stability modes, 20-setting slider, per-source 4×4 reference/variant codes and P1/P16 roles.
- Chromium Playwright `test_v53_browser.py`: **16/16 interaction regression checks PASS**, including all roles/source locations/edge types, rank6/female and rank7/male selection, viewer toggles, code slider, witnesses, and no JS exceptions. To work in restricted environments uses `page.set_content` from a locally read self-contained HTML file.
- `build_v53.py`, `build_lab_v53.py`, `write_docs_v53.py` produce the v53 role/candidate/stability summary files deterministically; twenty thousand source-image neighbor controls reproduced from seeded RNG.
- Deterministic `lagado_v53_motif_robustness_bundle.zip` has **24 members**, SHA256 **6b1d1db353a51a5af41c3925582285071fa65ed4bb9f6c9ec8df64ff55c177ed**; two independent packings give identical hash, ZIP CRC and each member SHA256 verified. Fresh-directory archive extraction plus rerun of script, viewer, report, browser test reproduces six derived assets byte-for-byte, including **16/16 browser PASS**.
- Data: `lagado_v53_11_motif_robustness.csv`, `lagado_v53_200_atom_stability.csv`, `lagado_v53_256_dormant_neighbors.csv`, `lagado_v53_17_motif_atom_variants.csv`, `lagado_v53_three_anchor_structures.csv`, full ASCII v53, report, results JSON, tested HTML screenshot. Original source pixels/previous versioned ledgers unchanged; retired legacy marker absent from new derived reports.

## Conclusion and next
The M/N quartet shows lower sensitivity to *first-scan parameter perturbations* than the two user-prioritized 3-glyph shared centers. This is a source-image processing robustness observation ONLY, not proof of a chemical nucleus, atomic ring, codon, or historical source cipher. Eleven connections do not stand out reliably from 256 other dormant adjacent cells. Next evidence priority is a complete photograph covering K8–L9, M8–N9 and I15–J16, using the exact locked extraction recipe and independently held-out image. No further routing or arbitrary bond promotion.
