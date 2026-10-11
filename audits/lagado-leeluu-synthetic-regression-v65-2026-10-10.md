# LEELUU Test 065 — Synthetic glyph-extractor regression
Date: 2026-10-10
Parent: audits/lagado-leeluu-commons-source-acquisition-v64-2026-10-10.md

## Scope
This test validates coordinate handling and sensitivity of the exploratory Test064 4x4 encoder only. It does NOT test real 1726 glyphs, independently photographed shapes, chemistry, DNA, or provenance.

## Runtime observations
Current working directory contained no original `lagado_16x16_source.png` or Commons PNG. Direct HTTPS request to upload.wikimedia.org failed DNS resolution. No genuine holdout comparison could run.

A synthetic 256x256 grayscale atlas was constructed as 16x16 cells of 16x16 pixels, with black inner squares at K8, L8, M8, N8, M9, N9 and otherwise white background. The Test064 crop and 4x4 code algorithm was exercised.

## Results: 5/5 PASS (synthetic fixture)
1. Target extraction: six target addresses each cropped as 16x16 and center black/corner white.
2. Unmarked control J8 encoded as sixteen zero bits.
3. Identical fixture copies generate zero Hamming distance at all six target glyphs.
4. Change inside M8 generates nonzero Hamming disagreement only at M8; other five targets remain unchanged.
5. Coordinate conventions: row K maps to zero-based row 10, column 8 maps to zero-based column 7.

Implementation test code is in `tests/test_leeluu_065.py`; it uses synthetic data and explicitly does not assert historical source validity.

## Five-layer outcomes
L1 image source: BLOCKED by unavailable image bytes.
L2 geometrical extraction: synthetic regression PASS; genuine comparison HOLD.
L3 grid address: synthetic regression PASS; real registration HOLD.
L4 neighboring relationships: no real-image evidence, HOLD.
L5 semantic mapping: UNVERIFIED.

Next gate: both authentic images and manually verified bounds in same runtime; compare against frozen v52 extractor and match capture provenance before publishing real lower-row statistics.
