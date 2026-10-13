# KET Generative I/O — 3D WASM v0.4 / Vector Point `0.-+.`

**Status:** new, additive application. **Frozen KET v2.0 remains untouched.**

The user's Rule 03: **each independent toroid may occupy a vector point `0.-+.`**. This version interprets that token as independently selectable signed `(x,y,z)` coordinates, each chosen from `{-1,0,+1}`. This 3D parsing is an implementation convention rather than a unique theoretical decoding. There are 27 distinct points for each toroid, 729 ordered pairs. Coincident centers may overlap visually but **do not merge toroid identities or send messages automatically**.

## Geometry, cells, and networking

- Torus A and B each retain **one open through-hole**, without an external enclosing box, wall or filled seventh position (Rule 01: `4+3 = 6 symbolic boundaries + 1 hole`).
- Independently chosen port A and port B lie in `0..359`. Optional logical link modes are `OFF | A→B | B→A | BOTH` (Rule 02).
- WASM places each torus by **`center_xyz = spacing × signed_vector_xyz`**; surface and radial geometry remain local to each center.
- Selected signed vectors are not additional kernel cubits. Each toroid retains **360+3+3=366 frozen logical addresses**. The signed speed-controller commands `--+` and `++-` still close exactly at 360° after 360 ticks, with baseline rate restored.
- Each toroid owns 360 × 1..5 derived transient cells with deterministic {-1,0,+1} cellular states, six possible lattice neighbors, seeded spontaneous activity, and next-generation delivery for enabled source-port transmissions.
- The function names `set_gap/get_gap` remain from v0.3 for WASM compatibility, but **now control *vector spacing***, not guaranteed body-to-body clearance. If selected centers coincide, shells can visually overlap without changing model identities.
- Glyphs preserved: seven ordered amplitudes with two independent Greens, three carriers, pinned zero, and **`123 {{45/|\54}} 678`**.

## Source files in this GitHub directory

- `src/vector_toroid.c` — real WebAssembly C simulation and signed vector placement exports.
- `index.template.html` — interactive WebGL2 / software 3D HTML page with six signed selectors, animation, seed/reset/step, communication gate, and JSON/CSV/PNG exports. Contains `__WASM_BASE64__` and `__WASM_SHA__` build-time placeholders.
- `build.py` — injects the compiled WASM binary, producing **fully offline `index.html`**.
- `test_vector.mjs` — builds on the v0.3 controller tests with signed-center and coincidence checks.
- **The compiled standalone HTML, actual wasm32 binary, input/output browser receipts, native 3200×1800 SVG blueprint, 3D preview, detailed 41-check suite and SHA-256 manifest are in the separately delivered conversation ZIP** `KET_Generative_IO_VectorPoint_3D_WASM_v04.zip`; this README does **not** claim those binary assets are committed here.

## Build

Requires clang/wasm-ld, Python 3 and Node.js at build time. The generated HTML requires only a modern browser and runs offline.

```sh
clang --target=wasm32 -O3 -nostdlib -fno-builtin \
 -Wl,--no-entry -Wl,--export-all -Wl,--export-memory \
 -Wl,--initial-memory=393216 -Wl,--max-memory=16777216 \
 -o vector_toroid.wasm src/vector_toroid.c
python build.py
node test_vector.mjs
```

The companion ZIP was built from the released local source, with WASM SHA256 `58bb38a89e78249562b0e64d4cf734fa3a60b5e02252a4b15371e0ad0517b440`. Rebuilding from committed GitHub source should be tested independently because toolchain environment and source comments can vary; do not assert byte-identical compilation without checking the digest.

## Executed results for the companion release

- **41/41 WASM structural/dynamic assertions PASSED**. Independent signed vector points, all 27 options each, coincidence without identity merger, OFF zero cross-transfer, both transfer directions, deterministic 360-tick playback, 360° phase closure, repeatable state digest.
- Chromium browser via an in-memory HTML page: **PASS**, no JavaScript exceptions. A `(0,+1,−1)`, B `(−1,0,+1)`, ports A:99/B:355 passed a directed transmission. Both placed at `(0,0,0)` with gate OFF exchanged zero messages over 360 ticks, retaining distinct cell arrays. Receipt export JSON/CSV checked.
- WebGL2 context was unavailable in that test environment. The **software projected 3D of the same WASM-generated positions** was browser-tested and screen captured. GPU hardware shader visual QA is still outstanding.
- Native editable 3200×1800 SVG generated from actual WASM positions at generation 84; SVG XML parsed, release ZIP CRC and member hashes verified.

## Links

- [Rule 01 — Six boundary positions + retained hole](../../architecture/KET_RULE_01_NO_EXTERNAL_BOXES_20261013.md)
- [Rule 02 — Optional twin toroid gap and information exchange](../../architecture/KET_RULE_02_TWIN_TOROIDS_OPTIONAL_GAP_IO_20261013.md)
- [Rule 03 — Signed vector point `0.-+.`](../../architecture/KET_RULE_03_SIGNED_VECTOR_POINT_0_MINUS_PLUS_20261013.md)
- Frozen KET controller pin: [de8f8b80aba3a73dd371811f6b4be39df92e45ce](https://github.com/DavidWise01/oasis/commit/de8f8b80aba3a73dd371811f6b4be39df92e45ce)

**Scientific limit:** symbolic 3D generation does not demonstrate literal Planck-scale physics, cosmic toroidal topology, or instantaneous physical message transfer.
