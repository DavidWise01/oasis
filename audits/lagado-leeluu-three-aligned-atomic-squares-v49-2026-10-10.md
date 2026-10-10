# LEELUU Test049 — Backward extraction of three aligned source-glyph squares
Date: 2026-10-10
PARENT: audits/lagado-eleven-atomic-motifs-reverse-peel-v48-2026-10-10.md
STATUS: EXECUTED / 15 OF 15 BROWSER CHECKS / 256 ADDRESS INTEGRITY / GEOMETRIC MODEL ONLY

## Discovery (source graph model vs proposed links)
Test048's last-surviving candidate-only connected tree N8—M8—M9—N9 contains THREE of the eleven engineer-selected dormant original-grid neighboring-cell pairs: M8--N8 rank1, M8--M9 rank2, and M9--N9 rank8. The missing fourth side, **N8--N9 (v22 edge e353)**, is a PREEXISTING one of the 109 accepted raster-similarity MODEL bonds. These four edges form a 2x2 square M8–M9–N9–N8 ONLY IN THE COMBINED graph of accepted-model bonds plus the proposals. The unmodified accepted-only graph does not contain that four-cycle.
Work backwards along original source rows/columns reveals two more similarly candidate-completed 2x2 squares, all at column boundary 8/9:
(1) **M8 M9 N9 N8**: 1 accepted side N8--N9 + 3 proposed sides (ranks 1,2,8). Charges clockwise [0,0,0,+1]; chemistry labels [ee,ee,uu,uu]; colors [orange,purple,blue,orange].
(2) **K8 K9 L9 L8**: 2 accepted K8--K9 and K9--L9 + 2 proposed rank6 K8--L8 and rank7 L8--L9. Charges [0,0,0,+1]; mnemonic rank6 female/rank7 male share L8. Chemistry all ee; colors [green,orange,green,orange].
(3) **I8 I9 J9 J8**: 2 accepted I8--I9 and J9--J8 + 2 proposed rank5 I9--J9 and rank10 I8--J8. Charges [-1,0,0,0]; chemistry all ee; colors [white,purple,green,white].
No movement of actual glyphs or inferred physical bonds.

## Exhaustive complete square scan and topology proof
Enumerated ALL contiguous 2x2 original source-address squares with current v41 ATOM-role glyphs and all four sides among original 109 selected model bonds or 11 proposed adjacency links.
EXACTLY FIVE complete squares in the combined graph:
- C13 C14 D14 D13: 4 ACCEPTED model edges, 0 proposed.
- I15 I16 J16 J15: 4 ACCEPTED model edges, 0 proposed.
- I8 I9 J9 J8: 2 accepted, 2 proposed.
- K8 K9 L9 L8: 2 accepted, 2 proposed.
- M8 M9 N9 N8: 1 accepted, 3 proposed.
Thus original-only complete 2x2 squares =2; candidate-completed aligned squares =3.
For the 200-atom vertex graph:
- Accepted model only: E=109, connected components=93, independent graph cycle rank E−V+C=109−200+93=**2**.
- Combined: E=120, components=87, cycle rank 120−200+87=**7**.
The 11 candidate links therefore add five independent cycles, three of which are the 2x2 squares; others have longer source-graph paths. As previously reported, the 11 candidate links alone form an acyclic forest: 17 glyph vertices, six components.

Charge deltas along a closed cycle telescope to zero by construction, not experimental energy conservation. LEELUU ee/uu/ll, 8^8^5^3^1, and female/male ranks are user-defined symbolic interpretations. Color classes were trained on the same initial image and are not proven real chemistry. The available independently photographed second plate includes complete rows A-E only; none of the three lower-row square glyphs has complete independent image replication. No historical encoding or chemistry claim is justified.

## Reproduction / release
Versioned v49 local artifacts in lagado_v49_backward_tiles:
- build_v49.py (stdlib) verifies frozen v41 role counts, 109 accepted original model bonds, 11 nonoverlapping grid-adjacent proposed connections, components and independent cycles; exhaustively enumerates 2x2 squares; outputs full provenance rows and report;
- build_lab_v49.py (stdlib) compiles a full self-contained offline clickable 256-address SVG viewer with 109 original/model bonds solid vs 11 proposed edges dashed, three backward selection cards, per-glyph source model features, P1 and P16 witnesses.
- test_v49_browser.py: **15/15 real Chromium Playwright regression checks PASS** including 256 source addresses, exactly 109 and 11 separately drawn edges, moving backward to K8/I8, charges, P16 witness, and no browser JS exceptions; screenshot lagado_v49_preview.png.
- pack_v49.py (stdlib): exact **16-member deterministic ZIP**, verified CRC and individual SHA256 manifest; two independent pack runs yielded the identical archive SHA256 **29fb3c3f1395fd2c6ced633d9456a1983e67595bafb0ef197956c39dfb7cc41a**.
- lagado_v49_backward_three_squares.csv, lagado_v49_twelve_square_edges.csv, lagado_v49_summary.json, lagado_full_ascii_v49.txt, lagado_v49_report.md; four untouched copies of previous source CSVs.
No retired legacy marker in any newly derived text. Frozen source assets, original v22 109 model bonds and historic v41-v48 audits are unchanged.

NEXT: reverse into the two already accepted-only 2x2 squares C13 and I15, comparing stroke shapes to see which (if any) previously proposed adjacent motifs share source-extracted features. Do not promote candidate connections to source-observed or real chemical bonds.