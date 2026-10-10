# Lagado Test034 — Independent Plate Acquisition and Grid-Only Registration Gate
Date: 2026-10-10
STATUS::ENGINEERING_PASS::INDEPENDENT_ARCHIVAL_IMAGE_REPLICATION_PENDING
PREDECESSOR::audits/lagado-image-fidelity-registration-v33-2026-10-10.md
SOURCE_REFERENCE::1726 Swift Academy of Lagado writing-machine plate, 16x16 glyph grid

## Acquisition status
Paderborn University Library has a digitization of the Volume II 1726 illustration, Plate V / Part III: https://digital.ub.uni-paderborn.de/ihd/content/zoom/3082162
IIIF manifest: https://digital.ub.uni-paderborn.de/i3f/v20/3081557/manifest
The plate is visible through internet retrieval, but direct downloaded bytes failed in the analysis container (DNS/network restriction). **No independently digitized archival image was measured in Test034**, and this is not a positive or negative source-replication result.

## Frozen canonical model
- 256 source glyph slots = 208 active + 48 reserve; P16 witness unchanged.
- Reference source SHA256 bea5f699b53f9306f37708fc81edbd9491ecaf042cd3971c32497c376e0ae21f.
- 109 prior geometric model bonds unchanged.
- Frozen original seven loop-hole anchors I6 I15 K11 M5 N5 O10 P7, derived from one source scan and 20 existing extraction settings (margin 4/5/6/7 × threshold -10/-5/0/+5/+10).
- Retired annotation remains excluded from new text artifacts while historical append-only source and audit chain are preserved.

## New method
Pre-register original 16x16 grid lines at 17 evenly spaced vertical/horizontal positions. In raster of size 784x788, isolate only +-8 px grid corridors and calculate phase-correlation offset between original and separate-normalized candidate scan after cropping. Accept only integer-rounded correction abs(dx),abs(dy)<=9 with phase quality>=.5. Source glyph features, seven hole labels, and 109 bonds are excluded from the registration calculation. Save *both raw and corrected* measures, all image SHA256 metadata and QA pictures; external file provenance always must be manually authenticated. This method protects against picking registration based on desired anchor recovery but is only translation, not arbitrary projective transform.

## Six executed SYNTHETIC tests (same original scan moved in raster, NOT independent)
| Deliberate dx,dy | Raw exact pairs/208 | Grid-only corrected exact pairs/208 | Raw 7 anchors | Corrected 7 anchors |
| +1,+1 | 197 | 207 | 7 | 7 |
| +2,+2 | 193 | 207 | 6 | 7 |
| +4,+4 | 186 | 207 | 6 | 7 |
| -3,+2 | 186 | 207 | 6 | 7 |
| -5,-2 | 178 | 208 | 5 | 7 |
| +7,+1 | 178 | 207 | 6 | 7 |

All six translation offsets correctly recovered to nearest pixel using only pinned gridline corridors. 6/6 matching>=207 and 7/7 anchor-survival regression checks PASS. One edge glyph often loses a feature due to the artificial scan clipping during shift. This is a synthetic software-engineering validation, not statistical evidence of a hidden code or actual archival replication.

Synthetic full-page import test: original scan pasted into 990x990 mock-page and ingested via the actual external --scan/crop path. Both raw and registered 208/208 measurements and 7/7 anchors match. This verifies the code path but is not a genuinely independent digitization.

## Deliverables, QA and immutability
- Standalone offline HTML `lagado_replication_v34_lab.html`: original 256 source slots/7 anchors, upload a local page image, visually position fixed 16x16 bounding rectangle, preview, download 784x788 PNG, download JSON crop manifest, archive link, six measured synthetic control rows, explicit PENDING badge.
- Browser Chromium Playwright 11/11 checks PASS including file input, editable crop, 784x788 PNG download, manifest, reset, no JS runtime errors. Node JavaScript syntax PASS.
- Python `lagado_replication_v34.py`: --self-test or --scan, SHA provenance, fixed v32 ink extractor, preregistered grid-only shift, before/after per-208 measurements, original 7-anchor 20-setting stability, QA side-by-side images, status JSON. Deployed source also includes frozen `lagado_replication_v32.py`, source PNG, original v22 nodes and v30 raster masks.
- 13-file archive ZIP SHA256 a978fefc867738f319e2f31241b5dc553d8d2f3d8b45474daee6336d2f402091, all ZIP CRC and per-file manifest SHA256 validations PASS.
- Technical report `lagado_replication_v34_report.md`, synthetic-control CSV, browser screenshot and source builders.
- All new derived text entries checked to exclude the previously retired wrapper. No mutation of old data.

## Reproduction
Unzip Test034 artifact, run:
`python lagado_replication_v34.py --self-test --out synthetic_grid_QA`
For independently acquired real archive page, visually crop with offline lab then:
`python lagado_replication_v34.py --scan cropped_16x16_grid.png --crop 0 0 1 1 --provenance 'archive catalog citation' --out real_scan_check`
Inspect all 208 observations and original-vs-archive.png before interpreting any anchor disagreement.

## Decision
Engineering PASS; second-scan pixel comparison PENDING because original institution-hosted JPEG could not be downloaded. No historical cipher, neural, molecular or physical-time conclusion follows. Next priority: acquire the real archive image bytes and run the fully locked test, without adjusting thresholds or selecting crops based on seven-anchor outcomes.
