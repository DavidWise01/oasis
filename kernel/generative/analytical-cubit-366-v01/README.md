# KET / Analytical Cubit 366 — append-only v1 (2026-10-12)

**Status:** executed local *computational* candidate, not established physical quantum hardware or nuclear theory. A complete reproducible Python/SVG/JSON bundle was generated in the originating ChatGPT conversation; this GitHub entry records its contract and observed results (does not falsely claim the exact executables are uploaded here).

## Addresses and graph
- 366 nodes = 360 periodic surface cells + six C.A.T.G.N.O gates.
- A chosen implementation of the 360 surface cells is a 20-skin × 18-sector **2D periodic graph** (not only an ellipse). 360 vertices, 720 undirected edges, 360 faces; Euler characteristic 0; every cell degree 4; one connected component.
- Indices 0..249: 250 logical cubit addresses (software, not physical quantum qubits). Indices 250..359: 110 workspace/recycle addresses.
- Gate indices 360..365: C,A,T,G,N,O respectively, attached to torus surface indices 342,345,348,351,354,357. N denotes -, O denotes +; no physical force assignments for other controls.
- **One analytical cubit** is the output report of this 366-address workspace, *not an additional address*.
- Parent layout 100×3×20+6=6006 stays separate; a mapping between parent and the 366-node local workspace was **not** invented.

## Five-axis scalar and reversible moves
User literal: `a=1.161651×10^-366`. Let `V=(a,a,a,a,a)` on v,w,x,y,z and `P=||V||=sqrt(5)*a=2.5975306021306082006234×10^-366`. Then `||V/P||=1` (95-digit decimal normalization). `sqrt(5)*a` itself does **not** equal one.

Keep phase `1.75` as a raw scalar, units unassigned. **Illustration only:** if turns are later selected, fractional phase .75 is 270 degrees.

Opposed signed moves: `x-2, y+3`, then `x+2, y-3`: net (0,0).
- Exhaustive 8^5 bounded-box check: 32,768 states, 15,360 valid round trips (46.875%); paths leaving the box are rejected.
- Exhaustive 9^5 periodic-toroid check: 59,049 states, all 59,049 round trips restore their original states.

## Recycle-capacity consequence
For a single round of 125 independent two-player matches over 250 logical candidate IDs, a 110-slot trash workspace cannot hold all 125 losers. A deterministic **index-only placeholder** comparator retained 125 winners, 110 loser IDs in the live trash workspace, and transferred 15 loser IDs into a separate recycling ledger: `125+110+15=250` source IDs accounted for, no IDs silently destroyed. Comparator is **not** atomic binding energy or a physical survival law.

## Execution and limitations
Local package reports 30/30 structural and accounting checks passed and includes:
`ket_analytical_cubit.py`, `test_cubit.py`, `render_svg.py`, `results.json`, `KET_366_Analytical_Cubit_HD.svg` (2400×1580, native editable SVG), PNG preview, README and SHA-256 manifest.

**Unproven:** no physical hydrogen atom confinement, gamma/X-ray force mapping, gravity-wave sentience, nuclear stability, stellar evolution or 250-element predictions have been demonstrated; model scalar `10^-366` is not a physically measured length. Parent/child packing has not been specified.

Read-only source landmarks: `kernel/main-aligned/v34/sheet-42/toroid-v05-results.json`, `projects/project-god-egg-jane-analytical-gradients-toph-patricia-icarium-v35-2026-10-11.md`. Earlier frozen artifacts unchanged.
