# Lagado / LEELUU Test050 — Reverse Audit of Two Accepted-Only Atomic-Model Squares
Date: 2026-10-10
Parent: audits/lagado-leeluu-three-aligned-atomic-squares-v49-2026-10-10.md
STATUS: EXACT SOURCE-GRAPH SCAN PASS / SECOND-IMAGE PARTIAL CROSS-CHECK / NO EMPIRICAL CHEMISTRY

## Inputs frozen
- 16×16 engraved illustration in *Gulliver’s Travels* is a fictional word machine.
- 256 fixed source glyph addresses, with current user-defined partition 200 atoms + 54 operants + two witnesses P1/P16.
- Previously selected **109 model similarity bonds**, not independently observed chemical bonds, retained unchanged.
- **11 engineer-selected neighboring-glyph candidates** retained separately, none promoted to an accepted edge.
- Eight color classes, symbolic ee/uu/ll chemistry and 8^8^5^3^1 remain provisional user-level mnemonics.

## Exhaustive first-source 2×2 geometry audit
There are 225 potential 2×2 lattice squares, of which **166** consist of four current atom-role glyph cells. Among these 166:
- **2 accepted-only** 2×2 squares: I15–I16–J16–J15, C13–C14–D14–D13. Every perimeter edge in both squares was already among 109 v22 selected model bonds. Neither requires any of the eleven hypothetical links.
- **3 candidate-completed** 2×2 squares: I8 (2 original-model edges / 2 candidates), K8 (2/2), M8 (1/3).
- **161 remaining** full atom squares do not have a closed perimeter even under the existing eleven candidate proposals.

Rank all 166 by mean Euclidean distance of their four perimeter edges in the original frozen (vx,vy,z²) feature space. Sorted ascending:
| Origin square | Rank / 166 | Average feature-vector distance | Model sides | Proposed sides | Signed glyph charge sequence |
|---|---:|---:|---:|---:|---|
| I15 | **1** | **0.177931673** | 4 | 0 | 0,0,-1,0 |
| C13 | **2** | **0.217982209** | 4 | 0 | -1,-1,-1,-1 |
| I8 | 37 | 0.369423866 | 2 | 2 | -1,0,0,0 |
| K8 | 46 | 0.389930637 | 2 | 2 | 0,0,0,+1 |
| M8 | 51 | 0.402231848 | 1 | 3 | 0,0,0,+1 |

**The rank ordering is not an independent significance test** because the same source-model vectors helped select the 109 similarity bonds. This validates the model's self-consistency only.

## Atom/glyph structure
- Accepted square **I15,I16,J16,J15**: topology sequence 110,011,111,111; symbolic channels uu,ll,ll,ll; colors purple,red,white,orange; first-image extracted stroke segments 47, paths 36, junctions 4.
- Accepted square **C13,C14,D14,D13**: topology sequence 000,011,101,110; channels ll,ll,ll,uu; colors white,white,white,purple; stroke segments 39, paths 36, junctions 2. All four signed dot-charge labels are -1. They are classifier outputs, not electron charge measurements.

## Frozen second-photograph cross-scan check
The independently photographed print crop previously supplied by the user covers complete A–E rows only. C13,C14,D14,D13 all appear; I15–J16 do not. Reuse exactly the v35 registered-image / comparison CSV with **no retuning**.
- C13 four-glyph hole-count matches: **4/4**, all zero holes.
- C13 four-glyph junction-cluster count matches: **1/4** (C13 2→1, C14 0→1, D14 0→1, D13 1→1).
- Mean registered binary-mask Dice for C13 four cells: **0.336685**. Pixel correspondence is imperfect due to print/crop/threshold variations.
- This is cross-scan replication of the *same illustration*, not independent confirmation of historical chemistry, genetics, biological sex, physical charge or actual glyph-to-glyph chemical bonding.

## Reproduction, verification, integrity
Source-faithful Python build `build_v50.py` enumerates 166 eligible 2x2 squares and ranks by untouched vector records, tests role counts 200/54/2 and 109 original vs 11 candidate edges, emits all candidate/source positions, original 16-symbol codes, code-derived stroke summaries and report. `build_lab_v50.py` embeds the registered second-photo C13 crop into a **fully standalone offline HTML viewer** with original 256 cells, 109 solid accepted-model edges, 11 dashed candidate edges, five switchable squares, per-glyph metrics, vector-distance rank distribution, model/source distinction and photos. `test_v50_browser.py`: **19/19 real Chromium Playwright checks PASS**, including clickable glyphs, witness P16, functional model/candidate toggles, C13 scan crop display, I15 explicit missing scan, source code table and zero JS errors.
`package_v50.py` deterministic compressed archive **lagado_v50_accepted_square_bundle.zip**, **21 members**, SHA256 `8a6f57364d606d2d1eb2e483c0a571e7853b4325c419c94c20e36915c19acf4c`; member hashes, ZIP CRC, second identical packing PASS.
Additional outputs: `lagado_v50_all_166_squares.csv`, `lagado_v50_five_square_atoms.csv`, `lagado_v50_C13_independent_photo.csv`, `lagado_v50_C13_two_scans.png`, `lagado_full_ascii_v50.txt`, `lagado_v50_report.md`, `lagado_v50_preview.png`.
New derived text avoids previously retired wrapper. All previous source images and versioned audits unchanged.

DECISION: ACCEPTED-ONLY SQUARE MORPHOLOGY CATALOGED. NEGATIVE-CHARGE UNIFORM SQUARE C13 VS MIXED-ZERO I15 ARE MODEL FEATURE PATTERNS, NOT CHEMICAL COMPOUNDS.
NEXT: acquire a complete lower-row printed plate to independently compare I15 and the earlier I8/K8/M8 candidates; or run a prespecified out-of-sample image feature test focusing only C13 known-visible square, with image-registration variance reported explicitly.