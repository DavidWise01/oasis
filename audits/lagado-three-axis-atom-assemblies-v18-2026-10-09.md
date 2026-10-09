# Lagado Test 018 — Three-Axis Atom Assembly, 208 of 255+1
DATE::2026-10-09
STATUS::EXECUTED_EXPLORATORY::NO_VERIFIED_HISTORICAL_PLAINTEXT
PARENT::audits/lagado-xyz-squared-depth-v17-2026-10-09.md
SOURCE::v12_quad_vector+v10_stroke_junctions+v16_frozen_208_ACTIVE_MASK
IMMUTABLE_SOURCE::256_ENGRAVING_CELLS::P16_SINGLE_WITNESS
FROZEN_DOTS::1+1+2+(..=4)+8=16::NOT_USED_TO_BUILD_BONDS
NESTING::17⊂52⊂104⊂208⊂256::RESERVE_48

## Three independent image-geometric axes
Treat each active source-sign as one simulated atom, carrying:
- X=(quad_B+quad_D)-(quad_A+quad_C), left/right straightened-stroke length imbalance.
- Y=(quad_C+quad_D)-(quad_A+quad_B), upper/lower imbalance.
- Z²=[(J+1)/(S+E+J+1)]², J=straightened-stroke junctions, S=segment count, E=endpoint count from frozen v10. This is a squared virtual feature, NOT physical depth.
Normalize features on same original 208 atoms and compute squared 3-axis Euclidean distance. Use the *predefined lower 20th percentile of all 21,528 active pair distances*, threshold frozen from the global all-pairs distance distribution, for every original 4-connected active-neighbor pair (382). No v14 dot polarity/family or trained dot-edge feedback is used. Bond is a similarity edge, NOT chemical valence.
For XY ablation, calculate separate all-pairs 20th percentile using only X and Y.

## Observed
- 208 distinct active atoms, 48 untouched reserve entries, P16 single existing witness.
- 382 possible local neighbor pairs. **109** three-axis bonds; **109** XY-only bonds; **97** overlap, so 12 bonds removed and 12 introduced by including Z².
- **31** connected candidate assemblies with at least two atoms; largest **18** source atoms: A7 A8 A9 A10 B10 B12 B13 C9 C10 C11 C12 C13 C14 D11 D12 D13 D14 E14; **70** isolated atoms.
- Two connected four-corner squares: C13 C14 D13 D14, and I15 I16 J15 J16.
- Nested cumulative stages at **one fixed global threshold**, not reoptimized:
  - Capacity 17: 7 bonds, 4 assemblies, largest 5, 6 isolates.
  - Capacity 52: 24 bonds, 9 assemblies, largest 9, 19 isolates.
  - Capacity 104: 49 bonds, 18 assemblies, largest 13, 37 isolates.
  - Capacity 208: 109 bonds, 31 assemblies, largest 18, 70 isolates.

## Permutation controls (3,000 each, identical preset threshold and complete source atom vector packets)
| Null | Mean 3-axis bonds | p(null≥109) | p(null mean Z² contrast≤observed) |
|---|---:|---:|---:|
| Free source shuffle | 76.432 | .000333 | .006664 |
| Permute within individual rows | 87.954 | .001999 | .017328 |
| Permute within individual columns | 77.110 | .000333 | .002666 |
| Permute within individual 4×4 blocks | 88.663 | .002333 | .019327 |
| Swap *intact* active-mask-matched columns + permissible top/bottom flips | 97.727 | .006331 | .035988 |
| Swap *intact* 4×4 blocks with identical active-mask footprints | **108.606** | **.533489** | .033655 |
The intact-block controls preserve much stronger geometric correlations than independently scrambling members *within* blocks. Because entire regions were moved only when source active masks matched, the null has few possible rearrangements; nevertheless the full 3-axis bond count is unremarkable under it.

## Third-axis ablation (3,000 shuffles)
Fix all XY source features and locations; shuffle Z² only within 4-by-4 bins defined by the **quartiles of source X/Y features** (not geographic 4×4 blocks). Observed normalized mean Z² mismatch across neighbors 1.617488; null mean 1.952268, p(low)=.028657. Observed 3D bond count 109; null mean 100.024, p(high)=.015995. This is an **exploratory third-axis geometric signal** in the already-inspected same engraving, not independent confirmation of an encoded historical 3D mechanism.

## Reproducibility / presentation
Local self-contained **lagado_atoms_v18_bundle.zip**, SHA256 c08510fbb26e568e47e65d90edc7f6037faeb75fe710d02f8f551d50db2a6dcf. Includes build_lagado_three_axis_v18.py, immutable v10/v12/v16 source CSVs, source illustration, derived 208-atom CSV, 382-edge table, molecule table, statistics JSON, report, embedded-image offline interactive HTML and Chromium smoke test+preview.
The HTML provides 17/52/104/208 capacity switching, 3D/XY/XZ/YZ projection, bond and atom toggles, 208 selectable source IDs, P16 witness, relevant shuffle p-values, and source engraving. Node --check passed; Chromium Playwright set_content using system /usr/bin/chromium passed all 7 in-page checks, selecting A7, hiding edges, resetting to P16, and showed zero JS page errors. ZIP CRC PASS.
HTML SHA256 2dfa6594afc72b126334ad2f7e07031c15268672aff24cdf8afdafa1e1501bb4

## Interpretation
This is *image-derived, virtual atom-assembly simulation*, not physical atoms, an actual third spatial dimension, a decoded alchemical/cuneiform language, or verified plaintext. The central image extraction was previously shown sensitive to small crop/threshold changes (Test009); the new stroke junction Z² must be independently rescanned and tested. No semantic or historical truth-state upgrade.
NEXT_GATE::INDEPENDENT_HIGH_QUALITY_SCAN_WITH_PREDECLARED_3AXIS_JUNCTION_SCORE_AND_INTACT_BLOCK_NULLS
