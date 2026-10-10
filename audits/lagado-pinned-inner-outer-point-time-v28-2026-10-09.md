# Lagado Test 028 — Pinned CATG Inner/Outer/Point-Time Loop
Date: 2026-10-09
Status: ENGINEERING PASS, PATTERN ENRICHMENT NOT OBSERVED
Lineage: audits/lagado-pinned-CATG-2D-3D-4D-v27-2026-10-09.md

## New user-defined (not data-fitted) two-register operator
- Inner time: 2/3 and 3/5; signed step offsets (-2,+3) then (+3,-5), net (+1,-2).
- Outer time: 1/3 and 2/5; signed offsets (+1,-3) then (-2,+5), net (-1,+2).
- Point/vector time: 2/3+1/3=3/3=1, and 3/5+2/5=5/5=1; complete four-vector displacement = (0,0).
- Center-fixed path: (0,0) -> (-2,+3) -> (+1,-2) -> (+2,-5) -> (0,0).
- Nontrivial geometry determined **algebraically** by these coefficients: self-intersects at rational point (2/5,-1), signed lobe areas +2/5 and -2/5, total signed area zero and unsigned lobe area 4/5. These are exact geometric invariants of the *chosen operator*, not evidence of literal time or original encoded content.
- Signed roles remain framework-local: prior -1=2D, pinned CATG 0=3D, successor +1=4D/append-time. These labels are not historical timestamps or measured physical dimensions.

## Frozen input, zero graph changes
- 255+P16=256 source glyphs, 208 active and 48 reserve.
- 109 existing frozen graph similarity bonds, no added/removed bonds.
- 97 original connected 3-atom paths around 64 distinct center glyphs.
- Original row-major endpoint convention is not known historical chronology.
- Anchor the vector-clock overlay separately to each path's center. Image x increases right, image grid row increases down, so a positive clock y moves *up*. Evaluate the THREE nonzero intermediate virtual waypoints for intersection with original active source addresses. The final return-to-center is not counted as a new match.

## Results (original R0)
- 97/97 four-step paths close exactly by construction.
- 245/291 intermediate waypoint visits lie within the original 16x16 grid.
- 221/291 land on an active original glyph (221/245 of in-bounds).
- 57 active intermediate waypoints share the pinned center's provisional A/C/G/T symbol.
- The original time-ordered graph paths comprise 37 straight, 29 left-turn, 31 right-turn paths; none is an immediate graph U-turn. Therefore virtual inner and outer opposite displacements cannot be interpreted as a directly measured two-edge motion on this grid.

## Dependency-respecting D4 null (5,000 trials, fixed seed 28335528)
For each of 64 unique source centers, independently pick one of eight rotations/mirrors of the same four-vector clock, applied consistently to ALL original graph paths sharing that center. Original graph positions, active mask, source labels and original bonds are frozen.
| Measured virtual-waypoint score | Observed R0 | Null mean | one-sided plus-one p(>= observed) |
|---|---:|---:|---:|
| Within-grid proposals | 245 | 241.299 | 0.30394 |
| Active glyph hits | 221 | 217.241 | 0.32753 |
| Same provisional base as center | 57 | 58.351 | 0.57089 |
The eight globally rotated/reflected clock overlays yield active-hit counts [221,199,222,224,224,219,202,226]; R0 does not win. No measured source-grid enrichment.

For avoiding center dependency as a supplementary descriptive check, 64 unique source centers × 3 intermediate proposals = 192, of which 158 are in-grid and 144 hit active atoms.

Illustrative seed F6 [G] → F5 [G] → G5 [G] (v27 path w032): centered clock virtual waypoint addresses C3, H6 and K7 are all active; closure returns to F5. These are **virtual skip addresses**, not newly discovered chemical bonds or literal historic events.

## Validation / deliverables
Exact-rational Python checks for intersection and ±2/5 signed lobes; 8/8 dihedral zero-displacement checks; 97 pinned graph paths and 208 active nodes verified. Browser standalone HTML with select path, rotate/mirror, step timeline 0-4, SVG source-grid overlay, exact internal clock visualization and JSON export. Chromium Playwright tests PASS with no JS errors (F6 seed and predicted waypoint labels, orientation and stepping, 97 path picker, selected w001), Node JS syntax PASS, 11-file ZIP CRC PASS.
- `lagado_clock_v28_lab.html`
- `lagado_clock_v28_report.md`
- `lagado_clock_v28_paths.csv`
- `lagado_clock_v28_stats.json`
- `lagado_clock_v28_bundle.zip` SHA256 `2909f8651c84eca774a914b14ec7a4501d0dadcab8d229f3718c39251f205938`
- Included builder scripts and frozen v27 input tables.

**Decision:** The user-supplied fractions and signed offsets imply a reversible equal-area two-lobe point-time operator. Its source-grid overlays do NOT yet add independent information or show genuine time, actual atoms, genetic codons, or hidden text. Next falsification is to derive local circulation directly from original stroke geometry and test whether it aligns with the precommitted template on a separate scan.
