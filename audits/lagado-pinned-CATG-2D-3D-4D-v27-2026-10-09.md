# Lagado Test 027 — Pinned CATG reference and symbolic -1/0/+1 temporal graph
Date: 2026-10-09
State: ENGINEERING PASS / EXPLORATORY PATTERN STUDY / NOT DECODED

## Hypothesis
Instead of looking for four consecutive historical glyphs spelling CATG, treat CATG as a *pinned four-state alphabet at local zero*. Read each existing connected three-atom path as:
`-1::2D input (u) -> 0::3D pinned CATG center/witness (v) -> +1::4D or append-only time (w)`.
The labels 2D, 3D, 4D are simulated projection/observation and history roles, not measured extra spatial dimensions or historical chronology.

## Frozen inputs
- Source image: 255+P16=256 engraved cells, 208 active, 48 reserve.
- Graph from Test022: 208 nodes and **109 bonds**, unchanged.
- Pseudobase mapping from Test026: 00=A, 01=C, 10=G, 11=T from (H,V) image topology; C/loop bit is preserved as a separate witness. This is not a decoded DNA alphabet.
- Test024 center 12-channel state and H/C/V topology retained, including leading zeroes.
- Each of 97 unoriented two-edge walks u—v—w yields one triplet whose center is the pinned 0. Outer endpoints are assigned prior/later by source row-major position, an explicitly artificial ordering; reversing u,w is equally possible.

## Actual outcomes
- 97 distinct three-node connected paths through **64 distinct center sites**.
- 46 distinct provisional base triplets and 51 repeated instances.
- Most frequent strings GTT, TGT, GTG (6 each).
- Turn categories: 37 straight, 29 left, 31 right.
- First visual example: F6→F5→G5, provisional 'GGG'; F5 is center pinned 0. Earlier same-scan image robustness showed F6-F5 much more stable than F5-G5; complete triplet is not reliably reproduced.
- Nested 17/52/104/208 graph layers: 4, 17, 39, 97 two-edge paths.
- Tests do not assert literal CATG recovered from glyphs, new chemical atoms, a DNA codon, biological brain connectivity, or physical time dilation.

## Controls
2,000 independently seeded shuffles per layout, base identity packets moved while the **109 graph bonds and source coordinates** remain fixed, identical triplet counts recomputed each time.
| Control | Mean repeated triplet instances | one-sided P(null >= observed 51) |
|---|---:|---:|
| Free source shuffle | 53.697 | .84758 |
| Within geographic columns | 53.3805 | .80960 |
| Within original geographic 4x4 tiles | 51.3785 | .60120 |
| Shuffle intact 4x4 tiles of matching active-mask footprints | 52.125 | .78411 |
No enrichment of repeated codon-like triplets against spatially grounded controls.

## Forward prediction check
Hold out all source paths whose CENTER atom belongs to a geographic source 4x4 block. Smoothed categorical probability model predicts successor/future provisional base from center-only vs center+predecessor. Difference in heldout bits/path = **-0.157230148389**, so adding the supposed 2D past makes 4D successor prediction **worse**. No independent time-direction law emerges from the data.

## Artifacts and validation
Created `lagado_pinned_catg_v27_lab.html` standalone interactive SVG graph and three-atom pinned path inspector, 208-node and 97-path CSVs, heldout CSV, JSON stats, deterministic Python builder and Python UI builder, technical report and source-verified ZIP.
`lagado_pinned_catg_v27_bundle.zip` ZIP CRC PASS; stand-alone HTML `node --check` PASS. Chromium Playwright `set_content` 8/8 internal checks PASS, tested seed F6–F5–G5, next path, capacity52=52 nodes/17 paths, return capacity208=208 nodes/97 paths; zero runtime page errors. UI leading-zero 12-channel padding was corrected prior to release.

## Interpretation
A center-anchored temporal **analogy** and repeatable vector graph projection, not a historical translation. Reading order was imposed by image row/column sequence. All original sources and edges are preserved. No explanatory gain confirmed relative to strong nulls.
Next: test whether independent timestamp/direction data exist at all, or compare shape-relative 3D center features using a new high-quality engraving before proposing new time physics.
