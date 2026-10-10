# Lagado Test 035 — User-Supplied Archival Photograph, Partial Replication and Complete ASCII Kernel
Date: 2026-10-10
STATUS: PARTIAL SECOND-IMAGE SOURCE CORRESPONDENCE PASS; SEVEN ORIGINAL LOOP ANCHORS NOT VISIBLE; FULL REPPLICATION PENDING
PARENT: audits/lagado-grid-only-archival-replication-v34-2026-10-10.md

## Actual source
User uploaded an original photographed period-book plate image labelled "Plate.V. Part.III." and "Page.74". File was 2048x884 RGBA: SHA256 eba02d6a92ec424d39e4815ef484be91af63a90d052325c207750ea22561aadf. This is a second IMAGE, not a synthetic distortion of our earlier raster. Provenance externally unverified. It is cropped off below the top of row F, so columns 1..16 and **rows A-E complete** (80 sites), F incomplete, G-P absent. Seven original stable ink hole anchors **I6 I15 K11 M5 N5 O10 P7** are all outside image. No claims about independent recovery of the seven are made.

## Frozen architecture preserved
- 255 + P16 = 256 total source sites; 208 algorithm-selected active sites; 48 reserve; P16 pinned as existing original witness.
- The second-scan visible A-E cells contain **56 active and 24 reserve** frozen positions. Do not treat all 80 as selected atoms.
- Previously frozen V22 208-node model graph, 382 source-grid edges, 109 similarity-defined bonds (NOT chemical bonds), and V30 7-loop anchor index left unchanged.
- Old v30 208 scan: 1249 ink components, 9 holes across 9 glyphs, 7 original stable loop anchors and 113 junction-containing source glyphs, 0 extracted two-lobed figure-eight cases.
- 12-channel 9+3 cortex and CATG pinned + input/output dimensional/temporal role overlays remain user-designed symbolic models, not proof of biological or physical structures. Inner (2/3,3/5) vectors (-2,+3),(+3,-5), outer (1/3,2/5) (+1,-3),(-2,+5) cancel to (0,0) exactly by definition.

## Executed image comparison (user-provided real screenshot, not synthetic)
- Manually identify ONLY original printed ruling positions in screenshot: 17 vertical x=[375,416,456,498,538,579,622,663,704,745,788,829,871,910,950,992,1034]; 6 horizontal y=[554,599,640,681,723,764] bounding five full rows. This is an image-to-image *crop/registration hypothesis*, not independently audited geometric calibration.
- Each photocrop individually resampled into the frozen source's corresponding 784x788 tile. Only complete A-E rows evaluated. Reapply EXACT existing V32 ink thresholds/extraction.
- Across 56 visible previously active cells: exact enclosed-hole counts match **54/56**; exact candidate junction counts match **30/56**; both count classes match **30/56**. Uploaded image created one loop each at **E6 and E14** where original source parser recorded zero.
- Geometry check not tied to feature counts: compare 16x16 thresholded source ink occupancy masks via Dice at all 56 matched coordinates. Mean observed **0.37058**, vs 3000 within-same-row source-label shuffle mean **0.30258**, null 95% range [0.28315,0.32212], plus-one p=**0.000333**. Same-row nearest-original identification: 16/56 top1 and 30/56 top3. This supports **glyph correspondence between photographs**, not hidden reading, biological codon, or physical clock inference.
- Caution: different source scans, substantial page pixel blur/resizing and hand-measured printed rules explain why some ink annotations differ. Statistical p is conditional on the selected matching metric and this five-row comparison.

## ASCII integration and tested package
A complete 190-line / 7355-byte seven-bit ASCII kernel state was built: full 16x16 mask, marked A-E scanned vs F partial vs G-P unobserved, all 7 original loop anchors, P16 witness, nested 17/52/104/208 states, 16-register 1+1+2+4+8, eight pipeline stages, 208/382/109 macrograph, 3721/2518 stroke micrograph, hydrogen-like F6-F5-G5 graph, bridge A7-A8-A9-A10, 4-cycle I15-I16-J16-J15, 12-channel cortex and four-vector CATG clock, evidence gates and outstanding full-page requirement.
- Local output: lagado_full_ascii_v35.txt, lagado_partial_archive_v35_report.md, lagado_partial_archive_v35_cells.csv, lagado_partial_archive_v35_comparison.png, lagado_partial_archive_ascii_v35.zip.
- Full ZIP includes exact uploaded image bytes, original raster, original CSVs, earlier locked v32 extraction source, and repeatable compare_partial.py plus build_ascii.py, per-cell results and registration preview, manifest. 16-file ZIP SHA256 **6cb329ad258a569430864e65289b7a2558e7eec7ad8bf4acf3f8f22cb7e54829**. ZIP CRC+manifest PASS; runnable comparison recomputed exact results. Retired wrapper is absent from newly generated derived texts.
- No original raster, model labels or previous GitHub audits overwritten.

DECISION: SECOND PHOTOGRAPH TOP 5 ROWS COMPARED; INPUT STRUCTURAL CORRESPONDENCE SUPPORTED; SEVEN-ANCHOR REPLICATION NOT TESTABLE FROM CROPPED SCREENSHOT.
NEXT: user can provide lower book page/complete plate containing F-P; rerun pre-registered 20-condition hole/junction tests and source-graph correspondence under fixed settings.