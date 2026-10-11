# LEELUU Test 064 — Wikimedia Source Acquisition Gate
Date: 2026-10-10
Parent: Test063 five-layer holdout
STATUS: ARCHIVE SOURCE OPENED / LOCAL BYTES BLOCKED / PIXEL HOLDOUT NOT EXECUTED

## Verified
The Wikimedia Commons image page identifies The Engine (Gulliver).png as a **640 × 675 px**, approximately **175 KB**, publicly viewable PNG, including a full 16 × 16 illustrated symbol grid.
- Page: https://commons.wikimedia.org/wiki/File:The_Engine_(Gulliver).png
- Original file: https://upload.wikimedia.org/wikipedia/commons/6/6d/The_Engine_%28Gulliver%29.png
- 2014 upload 640 × 675 px (405 KB); 2016 pngout compression 640 × 675 px (175 KB). These are not independent photographs.
- Image could be opened in the source-viewing service; direct HTTPS acquisition in container was attempted twice, blocked by DNS/download failure. Hence **no local PNG hash, image crop, alignment, or comparison output** exists.
- The previously reported local source hash bea5f699...27c376e0ae21f in v62 is historical, not reverified here; original scan is also absent from the current environment.

## Deliverable
Added `tools/leeluu_test064.py` reproducible *exploratory* segmentation tool:
1. requires two real PNG files and explicit manually measured crop-grid bounding boxes.
2. prints each file SHA-256, dimension; exports target crops K8,L8,M8,N8,M9,N9.
3. computes 4x4 ink occupancy and per-cell cross-image Hamming values.
4. writes JSON and records limitation.
Run `python tools/leeluu_test064.py --commons commons.png --original original.png --commons-box LEFT TOP RIGHT BOTTOM --original-box LEFT TOP RIGHT BOTTOM --out results`.
The script is **not** a replication of frozen v52 segmentation, so outputs cannot be compared numerically to Test062 until calibrated; no controlled instrument transfer or photographic independence is asserted.

## Gate status
L1: Public original URL confirmed; local bytes HOLD.
L2: Geometric comparison NOT RUN.
L3: 16 x 16 composition visually visible; pixel registration NOT RUN.
L4: Lower-row adjacency NOT RUN.
L5: Physical / chemical / ancestral interpretation UNVERIFIED.

Next: obtain both PNGs in same accessible runtime and prove source independence before running frozen-v52 lower-row transfer and controls.
