# Lagado Test026 — CAT/G Pseudocodon Pattern Falsification
DATE::2026-10-09
STATUS::EXECUTED::ENGINEERING_PASS::GENETIC_ENCODING_NOT_CONFIRMED
PARENT::audits/lagado-cortex-signals-v25-2026-10-09.md
CAPACITY::255+P16=256::208_ACTIVE::48_RESERVE
ORIGINAL_GRAPH::208_NODES::382_GRID_NEIGHBORS::109_BONDS
SOURCE_PRIMITIVE::1+1+2+(..=4)+8=16::FROZEN

## Registered experimental mapping (NOT deciphered genetics)
From each already-frozen v22 3-bit topology H,C,V, map (H,V) to one provisional base: 00=A, 01=C, 10=G, 11=T; retain middle C bit separately as a cycle witness. Base counts among 208: A50 C26 G61 T71. No biological DNA, ancient molecule, or historical reading order is asserted.

Read 208 atoms in source-grid row-major order, and independently in frozen nested Gen0-outward rank. Three phases 0/1/2 each. Row-major frame 0: 69 triplets /37 distinct/32 repeats; frame1: 69/33/36; frame2:68/40/28. Nested frame0: 69/40/29; frame1:69/42/27; frame2:68/39/29.
0 of 52 aligned CATG 4-tuples in either order; there is precisely ONE *sliding* CATG in flattened row-major order at four source cells **I16 J1 J2 J3** (crosses image row boundary), and zero CATG of four consecutive source cells within one physical original row. No sliding CATG in nested order.

## Controls
2,000 Monte Carlo trials per condition; repeat same three-frame test and select MAX frame repeats in every null trial (frame-search correction).
| Null | Flattened max repeats mean | p(>=36) |
|---|---:|---:|
| unrestricted packets |31.7255|.018491|
| shuffle within source columns |31.6295|.015992|
| shuffle within source four-by-four regions |31.786|.022489|
| shuffle INTACT four-by-four regions, only identical active-mask shapes |32.73|.042979|
These are exploratory, from the same already-analyzed engraving, multiple measures and mapping choices NOT multiplicity corrected.

**Adversarial row-break-safe correction**: restart frame 0/1/2 in every one of the 16 source image rows, never concatenate a row end with next row start. Frame0:64 triplets,36 unique,28 repeats; frame1:60/34/26; frame2:52/33/19. Highest repetitions 28 vs intact-region null mean 27.404 and one-sided p=.41929. Therefore the apparent p=.043 flattened signal is not physically/geometry robust.

On the 109 original graph bond edges, 72 length-two directed paths (following original right/down source direction), 34 repeated 3-base paths, CAT paths 0 and ATG paths 0. Graph motif repetitions vs intact-region null mean 34.296, p=.657671: no special DNA-like triplets emerging from bonded graph.

## Decision
Computational parser and motif finder PASS. Structural pseudocodons can be indexed and inspected. NO evidence that Swift's fictional Lagado symbols encode DNA/codons or actual chemistry; one CATG string appears only after flattening an artificial row boundary. The exact CAT/G hypothesis is not supported by the frozen grid geometry. No semantic/inferred historical truth promotion.

## Artifacts and validation
Local full reproducible ZIP `lagado_codon_v26_bundle.zip` SHA256 01600a68baaff3eb5471b55c074842362050acf8e9d9ffad8d79f0517c73406d, includes source frozen v22/v24 tables and source image, reproducible Python extraction of pseudo-bases, boundary-safe adversarial reruns, 8,000+8,000 permutation trial setup, row-major and nested transcript, 208 atoms CSV, 2-order 3-frame codons CSV, directed-graph path CSV, JSON stats, full report, 1.6MB standalone HTML, preview screenshot and Playwright regression. ZIP CRC PASS, inline JS Node syntax PASS, Chromium Playwright `page.set_content` browser test 11/11 checks PASS (208 active, 48 reserve, 256 grid slots, 3 frames, CATG selection, P16 source, no page JS errors).

NEXT_TARGET::TEST_FROZEN_PSEUDO_BASES_ONLY_ALONG_ORIGINAL_CONNECTED_ATOM_BOND_PATHS_OR_INDEPENDENT_SOURCE_SCAN; avoid adding codons from nonadjacent flattened rows.
