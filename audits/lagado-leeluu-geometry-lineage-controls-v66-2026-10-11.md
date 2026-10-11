# LEELUU Test066 — Grid Geometry, Threshold, and Source Lineage Controls
Date: 2026-10-11
Status: SYNTHETIC REGRESSION PASS; HISTORICAL HOLDOUT OPEN
Parent: Test065

## Executed run
`python /mnt/data/leeluu066/test_leeluu_066.py` (Pillow installed). **10 tests ran, 10 passed, 0 failures in 0.012 s.**
Script in `tests/test_leeluu_066.py` reproduces the same regression assertions.

Tests:
1 exact copy hash/geometry zero mismatch
2 grayscale→RGB re-encoding changes PNG hash despite identical RGB image data
3 uncorrected 4-pixel horizontal translation detected
4 correct 4-pixel translation with crop bounds compensates exactly
5 incorrect crop bounds detected
6 stable ink thresholds across 96,112,128,144,160 on high-contrast fixture
7 near-threshold ink produces different 4x4 codes
8 contrast transform is not photographic independence; codes stable in fixture
9 one-pixel perturbation changes hash without changing six target codes
10 4x4 aggregation loses some genuine pixel-level variation

## Interpretation
Five-layer source/image controls are stronger, but source independence remains **unverified**. Image file SHA-256 difference alone proves byte differences only; does not identify different photographic captures. The 4x4 encoder can conceal local details.
Test uses **synthetic grayscale 256x256 atlas**, six hardcoded targets K8 L8 M8 N8 M9 N9, Pillow BOX resampling. It is not historical glyph evidence. Runtime warning: Pillow Image.getdata deprecated (still works; replace with get_flattened_data in future compatibility pass).

L1 archival bytes: HOLD.
L2 algorithm geometry: synthetic PASS; historical HOLD.
L3 registration: synthetic PASS; historical HOLD.
L4 adjacency: historical HOLD.
L5 physical/chemical/ancestry meaning: UNVERIFIED.

Next target Test067: require both historical image byte streams; preserve source hashes, check source-family duplicated artifacts and frozen-v52 extraction before any lower-row holdout claim.
