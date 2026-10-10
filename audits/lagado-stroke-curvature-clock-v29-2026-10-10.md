# Lagado Test029 — Original Stroke Curvature vs. Pinned CATG Clock
Date: 2026-10-10
STATE::ENGINEERING_PASS::FIGURE_EIGHT_NOT_OBSERVED::NON_SEMANTIC

## Frozen lineage and exact operator
Parent: audits/lagado-pinned-inner-outer-point-time-v28-2026-10-09.md.
Pinned operator is the user's CATG reference 0::3D with past -1::2D / future +1::4D analogy.
Inner fractions 2/3,3/5; offsets (-2,+3),(+3,-5) net (+1,-2).
Outer fractions 1/3,2/5; offsets (+1,-3),(-2,+5) net (-1,+2).
Point clock fractions 3/3,5/5 and full displacement (0,0).
The input clock is a self-crossing figure-eight at (2/5,-1) with two opposite signed lobes +2/5 and -2/5; those are exact consequences of the specified vectors, NOT image observations.

## Frozen image evidence
One scan of Swift's fictional Academy of Lagado illustration. Test012 frozen source straightened paths and Test022 node/edge tables used without changing classifications or bonds. Source capacity 255+P16=256 original cells; 208 active, 48 reserve; 109 frozen symbolic bonds. Test027 original 97 connected CATG-centered triplets/64 distinct centers untouched.
Across active glyphs: 2,099 source-extracted path polylines, 2,518 straight segments. 1,839 paths consist of one segment; 98 have at least two signed turns; 27 have mixed-sign turns; 8 have near-balanced total positive/negative turning (ratio difference/total <= 0.15) across glyphs B13,E3,F11,F8,G7,H2,H4,L15. **0 within-one-path proper crossings of nonadjacent segments**, hence **0 fully matched self-crossing figure-eight path motifs**. Different disconnected stroke components were not retroactively stitched.

## Null and stress tests
5,000 seeded signed-angle shuffles **within original n-turn count groups** preserve the full angular sample distribution and path complexity counts, but remove path-specific sign co-occurrence. Matched balanced paths original 8; mean null 18.4824, 95% 12–25; upper-tail p=1.0, lower-tail p=0.00079984. Opposite turn balance is actually *depleted* versus this weak independence null; not enriched. Because glyph traces have been simplified by an image extraction algorithm, no natural-law significance should be inferred from that depletion.

Among 8 balanced candidates, 3 are one of 64 pre-existing pinned center glyphs. Under 5,000 shuffles preserving center counts within original 4×4 source-image regions, expected overlap 2.096 and upper-tail p=0.34653: no unusual center association.

Jitter already-extracted normalized path coordinates by Gaussian 0.5px/1.0px in 240 seeded trials/level; mean balanced-count across original 98 eligible paths 8.417 and 7.579. Example H4:p0 survives 99.17% of 0.5px trials and 89.58% of 1px trials; other candidates often much less. These are **post-extraction-coordinate noise tests only**, NOT threshold re-extraction or an independent scan.

Only 38 paths have >=4 straight segments and can be compared to four-vector template windows. The lowest fitted similarity shape error allowing translation, scale, rotation, mirror and best contiguous window is I12:p4 error 0.35728, but it has no self-crossing and is not a figure-eight.

## Verification and artifact
Builder: build_lagado_curvature_v29.py. Interactive UI builder: build_lagado_curvature_v29_ui.py. Standalone viewer lagado_curvature_v29_lab.html shows all 256 source cells, 208 active glyph stroke sets, 8 balanced candidates, 64 center markers, 5000-trial shuffle comparison, and exact clock diagram. Source and CSV exports: lagado_curvature_v29_atoms.csv, lagado_curvature_v29_paths.csv, lagado_curvature_v29_controls.csv, lagado_curvature_v29_stats.json.
Playwright in-memory Chromium against system /usr/bin/chromium PASS **10/10 in-page checks**, source selection B13/F11/H4, graph region shading modes, original 48 reserve, no JavaScript errors. Inline JS node --check PASS. 17-file reproducible ZIP integrity SHA256 cf71a2eb6e73fdc56405e5c8a8f49ccab4ac3c3afad81811c46f3236ba442527; per-file SHA256 manifest verified, ZIP CRC PASS.

## Decision
Keep clock operator as mathematical symbolic overlay. Preserve observed curvature features as tentative source metadata. No material recognition of signed-area lobes or historical reading direction. Real next test should independently retrace the ink source at higher resolution/second printing and test for **actual self-crossings and equal-opposed signed lobe areas**, not fit a clock to already simplified paths.

AUDIT::APPEND_ONLY::OBSERVED_VS_OPERATOR_SEPARATED