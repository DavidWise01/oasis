# LEELUU Test062 — Two-Photograph Source-Geometry Holdout and Archival Lineage
Date: 2026-10-10 (user local).
Parents:
- audits/lagado-bridgeman-image-asset-verification-v61-2026-10-10.md
- audits/lagado-leeluu-atlantean-ocean-laboratory-v60-2026-10-11.md
STATUS: OFFLINE QUANTITATIVE HOLDOUT COMPLETE; LOWER ROWS F-P INDEPENDENT-SCAN GATE OPEN.

## What was actually compared
Two earlier locally preserved images of the **same Gulliver's Travels Lagado writing-machine illustration**:
- Original cropped complete 16x16 grid: `lagado_16x16_source.png` (784 × 788 px), frozen source SHA256 `bea5f699b53f9306f37708fc81edbd9491ecaf042cd3971c32497c376e0ae21f`.
- Previously user-supplied, registered SECOND image: `registered_A-E_only.png` (784 × 246 px), **only first five complete rows A through E**.
**NO** Bridgeman or Wikimedia image bytes were used in the numerical analysis. Existence of archive/reseller thumbnails is not an independent photographic measurement.

Frozen v52 extracts exactly 56 existing atom-role glyphs from A-E and 93 neighboring pairs. Frozen v53 preprocessing prediction derives from 20 controlled **single-original-scan** crop/threshold settings (4 margins x5 thresholds). No retuning by second-photo outcome was performed; one of the 20 settings is guaranteed source baseline. Glyph code is printed ink occupancy in a 4x4 reduced mask, not chemical composition.

## Executed predictive relationships
| Prespecified source predictor → second-photo disagreement | Observations | Spearman rho | Exploratory one-sided row-stratified permutation p (20,000) | 5-row-cluster bootstrap interval (10,000) |
|---|---:|---:|---:|---:|
| First-image per-glyph mean 16-bit code instability → second-photo vs source 16-bit Hamming difference | 56 glyphs | **+0.3025705** | **0.00684966** | [+0.13237,+0.54894] |
| First-image neighboring-pair distance instability → second-photo vs source pair-distance change | 93 adjacent pairs | **+0.0946466** | **0.19254037** | [-0.07319,+0.25835] |
Mean absolute 16-bit cross-scan glyph Hamming mismatch=**5.3393 bits /16**. Mean across-scan neighboring-pair distance change=**2.0753**.
A modest glyph-shape/processing transfer signal was found (conditional on five rows and one photo pair); no persuasive pair/bond transfer signal. Shared endpoints, only five rows, selection/analysis multiplicity and instrument-dependent code choices limit certainty. Correlation does NOT mean independent chemical verification.

## Eleven frozen proposals, only two measurable in A-E image
- Complexity rank 4 **C8-C9**, first scan Hamming 6, second scan 7; distance change 1; earlier v53 first-scan predicted jitter 1.20.
- Complexity rank 11 **A8-B8**, first scan Hamming 7, second scan 7; distance change 0; earlier v53 first-scan jitter 1.35.
Remaining **nine** of eleven original-image-proposed adjacencies have NO second-photo test, including rank 6 K8-L8 and rank1 M8-N8, and the first-image most stable square M8/N8/M9/N9. Nothing in this test validates the user-assigned oxygen/hydrogen/neon/nitrogen categories, two symbolic sexes, a DNA/isotope signature, an Atlantean origin or a stable electrum molecular enclosure.
109 frozen source-image-similarity MODEL bonds and 11 separate engineering candidate adjacencies remain unchanged. 256 addresses=200 source-atom roles+54 operant roles+two witnesses. Test062 is not a new classification or physical bond test.

## Independent-image lineage findings; NEW OPEN-SOURCE CANDIDATE
Official Bridgeman AFF3514779 confirms the titled artwork and lists 4961x4932 px licensed source. Archive link:
https://www.bridgemanimages.com/en-US/english-school-18th-century/the-writing-machine-from-the-academy-of-lagado-balnibarbi-in-travels-into-several-remote-nations-of/nomedium/asset/3514779
MeisterDrucke preview credits Bridgeman. It is a syndicated presentation and has no independently attested capture lineage.
NEW candidate: Wikimedia Commons `The Engine (Gulliver).png`, public-domain image **640 × 675 px** and source listing 1726/Swift, uploaded 2014; visual full original grid, public:
https://commons.wikimedia.org/wiki/File:The_Engine_(Gulliver).png
Full image shown in the archive viewer resembles the same original engraved glyph arrangement; **its scan/capture provenance is not independently documented in the Commons record** and it is NOT yet demonstrated separate from AFF3514779 or the local original crop. 2016 PNG recompression of its original 2014 file does not make an independent artwork image. The full PNG was not obtained as local bytes because container internet/DNS access is unavailable. **Do NOT** call it a validated second full capture, claim pixel-level alignment or count it as the lower-row holdout. This source can be downloaded manually from Commons for next experiment, noting file SHA/rights.
Different artistic depictions of the Academy (e.g. 1850s French academy scene) do not contain the identical 256-cell plate and cannot be treated as a glyph-wise holdout; see:
https://commons.wikimedia.org/wiki/File:Willmann,_Colin,_%26_Outhwaite,_Gulliver_in_the_academy_of_Lagado,_cph.3b18908.jpg

## Test062 user artifacts; executable checks
Local `/mnt/data/LEELUU_v62_lineage_holdout/`:
- `LEELUU_Source_Lineage_Lab_v62.html`: 721KB fully offline interactive 256 source-cell atlas, all 11 proposed motif rows, interactive 56-glyph and 93-edge scatter plot, source image and second-photo overlay/individual inspection, claims/provenance statuses, exportable Test063 next evidence gate.
- `analyze_v62.py` deterministic holdout stats, 20k within-source-row permutations and 10k five-row cluster bootstraps.
- `build_lab_v62.py`, `test_browser_v62.py`, `pack_v62.py`, `write_report_v62.py`, frozen earlier extractor and node/edge/source-color datasets.
- Original 16x16 scan AND the A-E photograph are included; **NO unlicensed Bridgeman scan** included.
- 29/29 REAL Chromium/Playwright browser checks PASSED in this session, with no JS errors.
- ZIP `LEELUU_v62_Source_Holdout_Bundle.zip` 27 members, SHA256 `3a6bd8a0c4c75bab8900719f3e8cdc58ae3a203406275c556d03b7b119118fed`, ZIP CRC and SHA256 member manifest verified. HTML SHA256 `7dd0029df643abfe52e222c474097f472e8db148d386271b555d2e521ecd9287`.

## Next target 063
Get the public-domain Commons PNG source bytes or a distinct authenticated full-resolution institutional capture and establish its provenance. First test whether it is simply resized/high-contrast reuse of our original image via source-level alignment, pixel identity and photographic artifacts, **before** interpreting a shared visual pattern as replication. If a genuinely separately captured F–P photo exists, prespecify holdout extractor with fixed settings and verify K8–L8 plus M8/N8/M9/N9 and matched other grid-neighbor backgrounds; report uncertainty. Without independent F–P pixels, gate remains UNMET.

DECISION: TWO-PHOTO_A-E_GLYPH_ROBUSTNESS_PARTIALLY_SUPPORTED; TWO-PHOTO_EDGE_REPLICATION_NOT_SUPPORTED; FULL_F-P_INDEPENDENT_IMAGE_REQUIRED; SOURCE_ATOMIC_CHEMISTRY_UNVERIFIED.
