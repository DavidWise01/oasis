# Lagado Test030 — Original Ink Contour Falsification (2026-10-10)

STATE: ENGINEERING_PASS / FROZEN_SOURCE / NO_FIGURE_EIGHT_DETECTED
PARENT: audits/lagado-stroke-curvature-clock-v29-2026-10-10.md

## Frozen source and excluded annotation
One 784×788 raster of the fictional Academy of Lagado engraving. Original 256 sites; 208 active glyphs, 48 reserve, P16 witness. Existing graph's 382 spatial neighbor edges and 109 model bonds unchanged.
Legacy EE wrapper omitted from all new Test030 derived artifacts. Original source image, historical versioned outputs, and prior audit files remain unchanged.
CATG pinned inner/outer/point-time loop mathematically closes with equal opposite ±2/5 lobe areas; this is a definition of the chosen operator, not an original ink observation.

## Original ink recovery protocol
Read original image cells with original v11 ruler-line exclusion (25×1 and 1×25 morphological openings), 5px margin, grayscale threshold min(160, median−36), remove dark pixel components of size 1–2. Count white-space ink-enclosed holes by OpenCV contour hierarchy with area≥2.5 px². A true two-lobed candidate requires two holes **inside the same connected dark ink component**, ratio of hole areas≥0.80, and candidate skeleton junction cluster. Do not mistake outer ink outline winding or branch intersections for pen direction or true crossings.
Repeat 20 sensitivity conditions = crop margin [4,5,6,7] × threshold offset [-10,-5,0,5,10], same scan.

## Measured results
- All 208 active glyphs processed.
- 1,249 disconnected dark ink components.
- Exactly nine enclosed holes across nine different glyphs H9,I6,I15,K11,L3,M5,N5,O10,P7.
- Seven hole-bearing glyphs maintain a hole in all 20 settings I6,I15,K11,M5,N5,O10,P7.
- 113 glyphs show candidate skeleton junction clusters, 86 retain junction presence for all 20 settings.
- Across all settings only 9–11 holes recovered and ZERO glyphs with >=2 enclosed holes in one component; therefore zero balanced paired lobes or detected complete figure-eight candidates.
- A 2,000-trial within-4×4 hole-area shuffle preserving component counts yields 0 candidates in every trial; this control is DEGENERATE, incapable of demonstrating statistical enrichment. No significance claim.
- No signed pen circulation can be inferred from the algorithmic contour winding.

## Verification
17-file offline source+results bundle ZIP SHA-256 a6132f089224de116ccb2976b9ba3bfe9893b0486a9a8411fc1d894660d110d2; manifest digests and ZIP CRC verified.
Browser: Chromium Playwright 10/10 in-app data checks PASS; all/holes/stable/junctions filter counts 208/9/7/113; atom controls PASS, zero JS errors. Node JS check PASS.
Source SHA-256 bea5f699b53f9306f37708fc81edbd9491ecaf042cd3971c32497c376e0ae21f.
New derived text artifacts checked to exclude legacy wrapper. Source raster and frozen graph unchanged.

CONCLUSION: the theoretical double-loop has not been identified in the original continuous ink under this extraction method; observed ink holes and junctions are useful descriptive topology.
NEXT: lock these methods and repeat on independently digitized higher-resolution historical print to test robustness.