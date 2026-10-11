# LEELUU Test 063 — Five-Layer Lower-Row Glyph Holdout
Date: 2026-10-10
Parent: audits/lagado-leeluu-two-scan-source-lineage-holdout-v62-2026-10-10.md
STATUS: SOURCE IDENTIFIED / BYTES NOT ACQUIRED / INDEPENDENT-CAPTURE UNRESOLVED

## Source audit
Commons page: https://commons.wikimedia.org/wiki/File:The_Engine_(Gulliver).png
Direct PNG: https://upload.wikimedia.org/wikipedia/commons/6/6d/The_Engine_%28Gulliver%29.png
640x675 PNG. Wikimedia file history records 2014 upload and 2016 pngout compression, which are **not** independent captures.
The source page does not establish the image's scan/camera provenance relative to the original LEELUU source or Bridgeman.
The page and image are browser-viewable; attempts to retrieve PNG bytes in the analysis container failed due to network/DNS restrictions. No pixel comparison, no file SHA, and no measured cell results are claimed.

## Target set
K8-L8; M8-N8; M8/N8/M9/N9; negative-control nearest neighbors from matching rows. 16x16 naming/axis orientation must be matched to frozen source **before** any comparison.

## Five independent layers (per cell)
L1 / Raw ink: preserve unmodified image crops, bit-depth and geometric landmarks. Record provenance and SHA-256 of bytes.
L2 / Shape: compare glyph occupancy in frozen 4x4 (16-bit) representation; segmentation threshold jitter; endpoint/loop/hook topology, only when resolvable at available resolution.
L3 / Position: register image corners, assign row A-P, column 1-16 and quantify alignment residual. Reject rotation/transposition ambiguities before scoring.
L4 / Neighbors: calculate frozen adjacent-pair Hamming distance and four-cell-square consistency, with same-row randomized/matched controls. No chemical-bond inference.
L5 / Interpretation: provisional words, atom-role tags, element/chemical/DNA/ancestry labels are segregated as hypothesis, never observation. No promotion absent independent evidence.

## Decision gates
1. Verify source bytes + SHA. If unavailable: HOLD.
2. Compare captures using affine registration, downscale/contrast invariants and distinct dust/scratch/halftone or page-edge defects. If independent lineage not demonstrable: DUPLICATE-OR-UNKNOWN, not second holdout.
3. Freeze extraction settings from existing original; compare only pre-registered lower-row glyphs.
4. Report cell-level 16-bit Hamming, shapes, neighborhood errors and uncertainty, plus negative controls. If motifs do not outperform matched neighbors: FAIL for proposed special-neighborhood robustness.
5. Chemical / Atlantean / DNA meaning: UNVERIFIED regardless of image repeatability.

## Current outcomes
L1 SOURCE FOUND / BYTES HOLD.
L2 shape: NOT RUN.
L3 lower-row registration: NOT RUN.
L4 lower-row adjacency: NOT RUN.
L5 physical-meaning mapping: UNVERIFIED.
Test 062 A-E per-glyph correlation +0.3025705 and edge correlation +0.0946466 remain historic results, not retested here.
