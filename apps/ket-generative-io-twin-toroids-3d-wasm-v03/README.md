# KET Generative I/O — Twin Toroids / Rule 02 / 3D WASM v0.3

**Build:** 2026-10-13. **Scope:** additive interactive application prototype; frozen KET v2.0 source is not mutated. **Scientific status:** artificial generative cellular controller, not a physical Planck-scale, gravitation or cosmic-topology demonstration.

## User inference implemented

> yes its inference so to torroids can gap anywhere and share information or not

Two independent toroidal bodies remain separate (A, B). Both retain a central open through-hole, as required by **Rule 01: 4+3=6 symbolic boundaries + one hole**, without an external geometric cage or parent shell. Each body has its **own** 360 original surface ports + `--+`/`++-` six control positions = **366 fixed logical addresses**. There is **no sharing or multiplication inside either frozen register**. Runtime cellular samples (up to 5 radial layers) are derived data only.

- `gap`: independently adjustable minimum separation between the **two entire solid torus envelopes**; 0 through 3.5 on the UI (the WASM validator accepts up to 12). Do not confuse that clearance with the straight-line distance between arbitrary selected interface ports.
- `port A`, `port B`: each independently anywhere from 0 to 359 inclusive, mapping to toroidal angular positions `20×18`. They are interface markers, **not holes cut through the surface or new material cubits**.
- `OFF`: zero cross-toroid link message events, even if the bodies are close; each CA evolves locally.
- `A → B`, `B → A`, `BOTH`: optional directed messages from a cell that was excited **before the tick** to the counterpart's **next** cell-state buffer. A message is counted only if its selected source is excited and its gate direction is enabled. Incoming excitation does not consume or delete source state.
- Independent toroid state and clocks; the controller's angular state follows the frozen command schedule on **each** body and restores to 360° and 1°/tick after exactly 360 ticks when started at tick 0.

The **OFF** toggle is a software/networking gate only; it does not assert the absence of gravitational, thermal or electromagnetic interactions in actual physical systems. Nor is information transfer instantaneous in reality: this simulation applies an enabled message in the receiving cell's **next generation**.

## Implemented runtime

- Actual C compiled to a **wasm32 binary with zero imports**, embedded inline as Base64 in the standalone `index.html`; opens locally without CDN/network.
- WebAssembly computes **both 3D geometry and real synchronized cellular transitions**. Each torus contains 360×L derived cells, L=1..5; default L=3, **1,080 cells per torus (2,160 total)**.
- Individual CA state: 0 ready, +1 excited, −1 refractory. Each cell consults up to six nearest surface/radial neighbors, preserving periodic angles but not wrapping radial depth. Deterministic sparse local excitation is a *toy* seed process.
- WebGL2 renders WASM-generated 3D cell positions directly with GPU point sprites where available; interactive **software 3D projection of the identical WASM coordinates** is implemented and browser-tested as fallback.
- Orbit, zoom, change gate and gap live, independently choose endpoints, regenerate seed/layers, stimulate either port, step/continuous play/360 ticks, export JSON trace receipt, CSV trace and PNG viewport. UI source contains no network calls or telemetry.
- Independent opening geometry: nonintersecting standard embedded toroidal shells generated with major radius R>tube radius r, placed along world x with prescribed separation. The app does not create a cuboid cage or any additional surrounding closed mesh. Interface line appears only if the gate is enabled; visible line does not merge the mesh.

## Deterministic acceptance tests — actually executed

`node test_twin.mjs`: **40/40 assertions PASS**, including module validation/no imports, invalid geometry and port rejection, both toroidal cell counts, `OFF` no transmission, A-to-B and B-to-A transfer, bidirectional transfer, arbitrary endpoint 0–359, gap changes, 360-tick independent phase and velocity closure, zero transmissions with `OFF` across 360 generations, and bit-identical state digest on replay.

`python browser_test.py`: **PASS in Chromium** via in-memory page content. Confirmed actual WASM load, 2160 cells, full generation, position changes, any-direction gate change, port A=99 and port B=355, adjustable gap=1.90, stimulation with one A→B message, 360-tick playback, JSON and CSV exports, and **zero JavaScript exceptions**. Preview generated as `PAGE_PREVIEW.png` and `PAGE_PREVIEW_CONNECTED.png`; actual browser GPU WebGL2 initialization was unavailable so screenshots use the software 3D fallback. Do not claim GPU validation.

`node export_geometry.mjs && python render_blueprint.py` derives an editable native 3200×1800 SVG and 1600×900 PNG preview from **WASM-computed** positions at generation 84; it is a technical visualization, not an image of a real cosmic object.

## Rebuild

```bash
clang --target=wasm32 -O3 -nostdlib -fno-builtin \
  -Wl,--no-entry -Wl,--export-all -Wl,--export-memory \
  -Wl,--initial-memory=393216 -Wl,--max-memory=16777216 \
  -o twin_toroid.wasm src/twin_toroid.c
node test_twin.mjs
python build.py  # regenerates standalone HTML from template and WASM
python browser_test.py
node export_geometry.mjs
python render_blueprint.py
```

`index.html` is entirely self-contained; the exact SHA256 of the compiled module is embedded in it and reported by the audit. Other files support provenance and reproducible development.

## Source references

- [KET Rule 01](https://github.com/DavidWise01/oasis/blob/main/architecture/KET_RULE_01_NO_EXTERNAL_BOXES_20261013.md)
- [KET Rule 02](https://github.com/DavidWise01/oasis/blob/main/architecture/KET_RULE_02_TWIN_TOROIDS_OPTIONAL_GAP_IO_20261013.md)
- [KET v2.0 frozen source commit](https://github.com/DavidWise01/oasis/commit/de8f8b80aba3a73dd371811f6b4be39df92e45ce)

**Not a physics claim:** the symbolic hole and optional link are modeling semantics. Standard toroidal topology does not prescribe whether two physical objects exchange messages or which coupling channels exist. When a gate is `OFF` our model inhibits one defined cross-cell message mechanism; the model cannot establish complete isolation in nature.