# Lagado Test033 — Synthetic Scan-Fidelity Gate
Date: 2026-10-10
STATE::ENGINEERING_PASS / SECOND_ARCHIVAL_PIXEL_SCAN_PENDING
Parent: audits/lagado-independent-digitization-replication-v32-2026-10-10.md
This check is a synthetic quality-control experiment on ONE original grid image. It is NOT an independent historical plate measurement. The remote Paderborn image acquisition remains blocked in the execution container.

## Frozen source and model
Original source SHA256 bea5f699b53f9306f37708fc81edbd9491ecaf042cd3971c32497c376e0ae21f.
Frozen 255+1=256 source positions, 208 active atoms and 48 reserve. Prior 109 model-selected graph bonds unchanged.
Seven frozen original-scan ink-hole anchor sites I6,I15,K11,M5,N5,O10,P7.
For each of 20 synthetic same-source raster variants, redo Test030 exact *canonical* hole count and candidate junction cluster count for all 208 cells; for each seven pinned sites redo the 20 original crop-margin/threshold extraction conditions with zero tuning.

## Observations
|Same-source raster scenario|Both original feature counts matched /208|Seven pinned loops surviving all 20 settings|
|---|---:|---:|
|Unmodified|208|7|
|Translate(+1,+1)|197|7|
|Translate(+2,+2)|193|6|
|Translate(+4,+4)|186|6|
|Translate(-3,+2)|186|6|
|JPEG quality95|198|6|
|JPEG quality80|182|7|
|JPEG quality60|167|7|
|Gaussian blur sigma0.6|168|5|
|Gaussian blur sigma1.2|108|2|
|Gaussian pixel noise sigma4|190|7|
|Gaussian pixel noise sigma10|170|5|
|Gamma0.85|156|5|
|Gamma1.2|152|6|
|Downsample to90% then enlarge|168|7|
|Downsample to75% then enlarge|167|6|
|Downsample to60% then enlarge|149|4|
|Downsample to45% then enlarge|121|4|
|Minor perspective 2px|166|6|
|Minor perspective 4px|147|5|

In four simulated translation cases, phase-correlation shift estimation recovered the ground-truth shift to about 0.001px; applying the inverse correction restored **207/208** original two-feature source-classifications AND **7/7** anchor survival in all four. This is strong engineering evidence for *same-image translation correction*, not a guaranteed registration method for photographs of different physical prints. The 1.2px blur test destroys five of seven loop classifications. JPEG-quality 60 preserves 7/7 anchor classifications despite decreasing exact glyph-level agreement to 167/208. These outcomes are not population prevalence estimates; parameters were chosen for stress-testing.

## Release
lagado_fidelity_v33_lab.html: single offline HTML with 256 source slots, 208 active states, scenario selection, hole/junction comparison, seven pinned site inspectors, registry corrections and 20-case chart.
Playwright Chromium 13 in-browser assertions PASS; zero JS errors. Original source graphic and all model edges preserved.
Full reproducible 17-file ZIP lagado_fidelity_v33_bundle.zip SHA256 d8c7e9c8386b07ed39fcbe440c8b7f9c494eb3ceaefd55d629114e4be3abd471. ZIP CRC and all manifest SHA256 entries verified. New derived text artifacts exclude previously retired annotation.
Files include source raster and previously frozen V30/V22 tables, new Python builder and UI builder, CSV data for all 4,160 source-cell scenario measurements, seven×20 scenario anchor results, JSON statistics, viewer and screenshot, original locked V32 archival runner, README and technical report.

## Archival readiness
Paderborn archive: https://digital.ub.uni-paderborn.de/ihd/content/zoom/3082162
The image JPEG is publicly identified but its bytes could not be fetched into this execution environment; there have been 0 completed pixel tests on the second scan. When provided a verified separate capture, lock crop to physical 16x16 borders and run:
python lagado_replication_v32.py --scan plate.jpg --crop x0 y0 x1 y1 --out independent_scan_check
Record scan SHA256, dimensions, crop, provenance, alignment QA and complete 208-site output. Never choose crop or thresholds solely to increase anchor hits. A second digitization of the same printed plate verifies morphological reproduction of that plate, not underlying genetic, atomic or time physics.

DECISION: 033 PASS AS SOURCE-FIDELITY ENGINEERING; REPLICATION UNRESOLVED, NO CIPHER CLAIM.
