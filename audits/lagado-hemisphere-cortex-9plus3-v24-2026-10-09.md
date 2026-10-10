# Lagado Test 024 — Dual-hemisphere 9+3 Cortex Projection
Date: 2026-10-09
Status: executed, graph visualization and statistical controls verified; exploratory **symbolic** brain analogy, not neuroscience or historical decipherment.
Lineage: audits/lagado-hydrogen-seeded-motifs-v23-2026-10-09.md

## User notation and 12-lane interpretation
User: `left hemi :: -3 | center cortex {{i::3::-1.0.+1}} | right hemi + 3 total 12, 9 + 3`.
Model: 3 negative vector-axis ports + 3 existing local H/C/V topology identity channels + 3 positive vector-axis ports = 9, plus a one-hot 3-register signed cortex gate (-1,0,+1) from the original frozen dot-charge sign = 12 **binary** lanes. These are **modeling assignments**, not established cortical/brain physiology. Source charge may still be ±2 but gate collapses to sign, while raw charge is retained.

Negative/positive ports indicate existence of a v22 BONDED neighbor with x/y/z² geometric feature below/above a node's feature, so **port values are functions of the frozen bond graph**. They are not blind evidence predicting the same bonds.

## Fixed source
255 + P16 = 256 source locations; 208 active, 48 reserve, cumulative capacities 17/52/104/208, original Test022 382 grid neighbor pairs and 109 similarity bonds unchanged, no new atoms. 
SHA256 frozen v22 nodes CSV: 75087bacb04f6af4a3d75c6b69fbb842d82157db2dffd91984422069067528d4.
SHA256 frozen v22 edges CSV: cdefbb32754755635b3e3bc6a19b8932437352a36d44ac4074e49fdf053d282c.

## Results
Printed-grid regions: left columns 1–7 (88 active), center columns 8–9 (32), right columns 10–16 (88).
Of 109 bonds: left-left 42, left-center 4, center-center 9, center-right 4, right-right 50. One original 18-node graph component spans left and right via cortex band; shortest route A7→A8→A9→A10 (original graph edge topology). The geographic path is not a corpus-callosum observation.

Gate state counts: −=43, 0=123, +=42. Distinct nine-channel signatures 87; distinct twelve-channel signatures 116; 23 nine-bit classes subdivided by adding gate. Empirical descriptive conditional entropy H(gate | nine-channel signature) = 0.751367 bits/atom; this describes distinguishability, **not new factual/historical information or out-of-sample prediction**.

Ordered original-graph two-edge triad paths sign −→0→+: exactly 2, C12→B12→B13 and C12→C11→C10.
4,000 same-graph randomized signed-gate label controls, atom positional mask and 109 edges fixed:
- global label shuffle mean 4.8792, one-sided p(null≥2)=0.946763.
- within-source-column shuffle mean 5.1147, p=0.953262.
- within-original-4×4-tile shuffle mean 2.7957, p=0.752562.
No enrichment of the proposed triplet pattern. Because previous v14 dot charges were already learned with neighborhood feedback, even a positive gate correlation would not automatically demonstrate independent coding.

## Verification and artifacts
Produced offline self-contained `lagado_cortex_v24_lab.html`, Python builder `build_lagado_cortex_v24.py`, UI builder, Test024 208-node / 382-edge / two-triad-path CSVs, JSON stats, full report, Playwright browser test and screenshot. `lagado_cortex_v24_bundle.zip` SHA256 67b1592758942a72548ffd5d55134020b6a2a494718b5d6acf5bc09829a9c20c. ZIP CRC pass and Node JavaScript parse pass.
Chromium Playwright `set_content` verified 9/9 in-page checks, 208 at capacity 208, **exactly 52** at capacity 52 (correct boundary check uses rank<capacity because P16 has rank 0), selected F6/A7, highlighted shortest cross-hemisphere route, gate coloring, bond visibility off/on, and zero JavaScript page errors.

Result is a usable annotated signal-routing overlay with 116 distinct local signatures, not a verified neural, physical-atomic or hidden-cipher mechanism.
NEXT: test cortex gate's incremental out-of-sample prediction of previously unused geometric features, without reusing labels/edges employed in constructing channel values, and independently replicate from a second high-resolution engraving.
