# SHEET 90 — 8:0:8:0:8:0:8 Toroidal Copper Box (WASM × SVG)

Append-only successor to SHEET89. This implementation resolves the user's notation **provisionally**:

- `8 0 8 0 8 0 8` → four 8-cell banks and three zero seams, 32 active octet cells.
- `9 9 9 9 9 9 9 9` → eight toroidal floors, with nine toroids on **each** floor (72).
- `3 per floor x y : z²` → three toroids for each of X, Y, and Z² per floor (3+3+3=9). This is a testable working interpretation, not a claimed unique decoding.

One parent box retains the 11 copper sublayers (L−5..L+5) and `{{−1::0::+1}}` center bus on every logical floor (88 symbolic copper traces). Signed floor address `z=floor−3.5` is preserved alongside `z²`, since squaring merges paired values. The actual C kernel in this directory compiles to a freestanding wasm32 module. The standalone SVG viewer embeds the binary (and can run directly from a local file), draws 72 elliptical ring projections and 120 moving lane markers, exports an SVG snapshot and JSON ledger, and offers floor/axis filters, speed, pause and reset.

The real WASM state-machine executes immutable lane indices 0..119, bounded floors 0..7, toroids 0..8, copper positions 0..10, and octet banks 0..3. Each completed orbital lap meets a 24-tick interpolated copper or floor via at the common orbit anchor. Every third transfer is an inter-floor via and advances the active octet; 0 gates count only between banks 0/1, 1/2, 2/3 (not wrap 3→0). Via and lane events are appended in the viewer's local ledger; export before resetting if retention across sessions is needed.

## Local validation (actual compiled artifact)

- Freestanding `clang --target=wasm32 ...` produced a **2633-byte WebAssembly binary**.
- `node test_wasm.js` executed the real WASM module for **1200 ticks; 31/31** checks passed. Across 144,000 lane-state observations: 785 orbit closures, 774 completed vias, 215 floor vias, 169 zero seam crossings; all 72 initial (floor,toroid) addresses populated and deterministic replay verified.
- `node test_svg_dom.js` ran the standalone HTML's actual embedded-WASM JavaScript under an instrumented DOM for 600 animation frames: **30/30** checks passed, including 72 SVG toroid groups, 88 displayed copper traces, 120 packet circles, all controls, and 1,200 WASM simulation ticks.
- `node --check`/inline JS parse passed and packaged ZIP archive CRC passed.
- Attempted Chromium headless rendering **timed out**, so browser paint and interactive graphical correctness remain unverified. An instrumented DOM is not a real browser.

## Reproduce

Get the complete package `sheet90_toroid_box_wasm_svg.zip` from this conversation. It includes the exact built `index.html`, `kernel.c`, `kernel.wasm`, `build_html.py`, `test_wasm.js`, `test_svg_dom.js`, complete `results.json`, README, and a SHA-256 file manifest.

Build: `clang --target=wasm32 -O2 -fno-builtin -nostdlib -Wl,--no-entry -Wl,--export-all -Wl,--strip-all -o kernel.wasm kernel.c`. Then run `node test_wasm.js` and `node test_svg_dom.js`.

**Scope:** This implements symbolic elliptical toroid projections, not literal 3D copper/EM fields, gravitational forces, fabrication PCB DRC, physically verified routing clearance, 9/6/1 scheduler execution, 60-position wave engine execution, or acknowledged packet delivery. Earlier OaSIs sheets are preserved rather than overwritten. Only the C source, audit and result summary are currently committed on GitHub; the full exact executable viewer and tests are in the ZIP.
