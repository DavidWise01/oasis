# SHEET 89 — WebAssembly vertical copper vias

Append-only upgrade from SHEET88, 11 copper sheets L−5..L+5 with the center tri-bus `{{-1::0::+1}}`. **Real WebAssembly (wasm32) executable** compiled from freestanding C; 1,628-byte binary. SVG remains browser rendering; WASM owns 120 lane positions, traversal phases, layer progression and portal transitions. At the route endpoint, each lane spends **24 ticks** interpolating between adjacent copper layers at one fixed portal. A new path begins at the destination via end. New lane identities remain 0..119, and 9 portal identifiers remain 0..8. Continuity holds in the 2D projected coordinate positions of the rendered via.

## Verified runnable local package

- `index.html` (self-contained embedded WASM; open directly on disk, no external dependency)
- `kernel.c` (freestanding C, authored for wasm32)
- `kernel.wasm` (actual compiled binary)
- `test_wasm.js` (Node loads and executes the actual wasm binary)
- `README.md`, `SHA256SUMS.txt`

Build: `clang --target=wasm32 -O2 -fno-builtin -nostdlib -Wl,--no-entry -Wl,--export-all -Wl,--strip-all -o kernel.wasm kernel.c`. Test: `node test_wasm.js`.

**Executed checks:** 15/15 assertions passed, with runtime invariants checked for every lane on 1,200 ticks. **785** route traversals and **774** completed vertical-via transfers; all 11 layers and all 120 lane IDs visited. Deterministic reset/replay passed. SVG embedded JavaScript syntax passed independent parse check. Package ZIP CRC passed. Browser interactive verification not yet run, nor collisions/clearance in physical 3D.

## Scope and provenance

This GitHub document is an implementation audit. The **complete exact tested executable/binary/viewer package is attached to the conversation as `sheet89_wasm_copper_vias.zip`**. The code is not represented as already uploaded to this repo by this README. Earlier SHEET88 is unchanged. The simulation does not model electromagnetic signal integrity, manufacturable PCB design rules, real 3D collisions, or physical gravitation.
