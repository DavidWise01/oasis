# KET Rule 03 — Independent Signed Vector Points `0.-+.`

**Established:** 2026-10-13 · **Authoritative user statement:** “exactly then each torroid can occupy vector point 0.-+.”

## Rule

Each toroid occupies its own **vector point** in the symbolic `0.-+.` coordinate space. Placement of one toroid does not establish the placement, identity, message permission, or state of another. The gap is therefore **an inferred relation of positions**, not an obligatory outside enclosing box or a source of messages.

## Additive 3D WASM implementation v0.4

Treat the literal `0.-+.` as a three-valued signed selector **per spatial axis**: `x,y,z ∈ {−1,0,+1}`. This is an **explicit implementation choice**, not a demonstrated unique mathematical parsing of the glyph.

- Each toroid has **27** possible signed vector-center positions (`3³`).
- Two distinct toroid identities A and B admit **729 ordered placement pairs** (`27²`), including shared center coordinates.
- Position in the visualization: `center(t) = vector(t) × spacing` for one nonnegative display scale. This does not change the torus's intrinsic geometry or cell-state neighbor graph.
- Distinct toroids at coincident centers do **not** merge, exchange messages automatically, or mutate each other's registers; their rendered cells may overlap.
- The visually derived clearance `|centerB-centerA| - 2(R+r)` may be negative for overlap; it is a diagnostic, not a barrier or a permission signal.
- Communication gate remains independent: `OFF | A→B | B→A | BOTH`, with port choices from 0 to 359 on each body. Gate OFF guarantees no modeled cross-toroid messages, **not** absence of all physical influences.
- Spatial positions, physical lengths, geometrical through-holes, and signed memory/control glyphs are different concepts. A vector's `0` coordinate is not a new kernel zero; `−/+ ` are sign selectors, not automatic `--+` or `++-` speed instructions.

### Bounds and invariants

- **Rule 01:** six mnemonic boundaries plus an unobstructed toroidal through-hole; no seventh wall, outer cage or external box.
- **Rule 02:** arbitrary surface ports, mutually independent identities, voluntary message exchange.
- **Rule 03:** independent signed vector positions, including coincidence without forced merger.
- **Frozen v2.0 unchanged:** 360 toroidal surface positions + 3+3 controls = **366 addresses per toroid**; the speed controller closes at 360 degrees after 360 symbolic ticks.
- The two Greens, seven ordered amplitudes, three carriers, pinned zero, original Chariot glyph `123 {{45/|\54}} 678`, and symbolic cellular state remain preserved.

## Tested new application overlay

Companion **KET_Generative_IO_VectorPoint_3D_WASM_v04.zip** (supplied separately in the conversation):
- clang-compiled no-import WebAssembly cell and 3D mesh engine, offline self-contained HTML, C source, Node assertions, Chromium interaction test, SVG/PNG generated from WASM coordinates and export receipts.
- **41/41 WASM assertions PASS**: 27 valid coordinate choices for each toroid, 729 ordered placements, vector independence, same-point occupancy, 360° control closure, deterministic replay, and logical messaging gates.
- Chromium: generated/signed vectors independently changed; arbitrary A:99/B:355 ports transferred A→B only while enabled; coincident `(0,0,0)` with OFF exchanged zero messages after 360 steps, with no JavaScript exceptions.
- Browser WebGL2 rendering was unavailable in the test environment; the real WASM geometry was visualized by the software 3D fallback. No Planck-scale or universal cosmic mechanism is claimed.

## Status

This document is an **additive forward design rule**. Freeze-pinned commit `de8f8b80aba3a73dd371811f6b4be39df92e45ce` and its files are not changed. Future implementation revisions go to additive paths under `apps/`. The physical meaning of the user's mnemonic beyond the signed-vector prototype remains speculative.
