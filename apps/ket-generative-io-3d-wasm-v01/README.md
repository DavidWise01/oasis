# KET Generative I/O — 3D WebAssembly v0.1

**Status:** implemented, tested, additive application layer. **Frozen KET v2.0 remains unchanged.**

## Open the app

Open **`KET_Generative_IO_3D_WASM.html`** in Chrome, Edge, Firefox, or Safari supporting WebAssembly and Canvas. It runs entirely offline, requires no external JavaScript libraries, and contains the compiled WASM binary inline. WebGL2 is the primary 3D renderer. If WebGL2 is unavailable, the app uses a Canvas2D software 3D projection of the *same WASM-generated mesh* (geometry and physics stay in WASM).

## Input contract

Edit JSON in the left panel and select **Apply & generate**:

```json
{
  "schema": "KET/GENIO/3D/WASM/v01",
  "input": {
    "seed": 42,
    "major": 2.3,
    "minor": 0.86,
    "twist": 0.16,
    "base": 1,
    "delta": 0.1,
    "ticksPerSecond": 6
  },
  "register": {
    "surface": 360,
    "controls": ["--+", "++-"],
    "amplitudes": ["RED", "GREEN", "BLUE", "ORANGE", "PURPLE", "GREEN", "YELLOW"],
    "carriers": ["WHITE", "BLACK", "GRAY"],
    "pinnedZero": 0,
    "chariot": "123 {{45/|\\54}} 678"
  }
}
```

The `register` object is **immutable**; attempts to alter it are rejected. `input` fields have strict numerical validation. The torus major radius must exceed the minor radius; base angular speed must exceed twice the rate increment.

## Output contract

- Browser output: actual 3D toroidal mesh generated in WASM: 48×96 smooth surface vertices, plus 20×18 sampled/address vertices = 360, with six control-port markers.
- Playback: Play/Pause, Step, Reset, Full circuit (360 ticks).
- Interactive viewport: drag to orbit, wheel/trackpad to zoom, adjustable tube radius and Green Chariot twist.
- Export: PNG viewport, JSON input/state/receipt and 360-tick trace, CSV sequence.
- Seed: deterministic pseudorandom field used only to shade the mesh; not a physical noise process.

## Physics and control specification

The application implements the existing **illustrative** KET control convention, not a measured celestial process:

- `s[k] ∈ {−1, 0, +1}` is the active signed command.
- `ω[k+1] = ω[k] + δ·s[k]`, then `θ[k+1] = θ[k] + ω[k+1]`.
- First six: `--+ ++-` = `--+++-`; second six (reuse same control addresses): `++- --+` = `++---+`.
- For baseline `1°/tick` and δ=`0.1°/tick`, first pass rotates `5.7°` (−0.3° phase lag), second `6.3°` (+0.3° phase lead), 348 neutral ticks yield **360°** and final `ω=1°/tick`, phase error **0°**.
- Model topology: 20 skins × 18 sectors = 360 logical surface vertices; E=720, F=360, Euler characteristic 0; control addresses 360..365; **366 total**.
- Green A2 and Green A6 remain independent slots; chariot glyph preserved **exactly**: `123 {{45/|\54}} 678`. Carriers White/Black/Gray and the pinned zero are *register lanes*, not additional geometric cells.
- LEVIATHAN `0root`, `N::CATGNO`, five operators, and previously frozen tracks unchanged.

## Executed validation

- C compiled to a genuine **wasm32 binary** with no runtime imports (4,714 bytes); embedded into the standalone HTML.
- Node/WebAssembly structural/geometry test **19 asserted checks**, 360-tick final closure verified.
- JavaScript syntax check (`node --check`) passed.
- Browser exercised via Playwright `page.set_content` because direct file and localhost navigation was restricted in the test environment; **no JavaScript exceptions**; JSON input, apply, full circuit, step/reset, JSON and PNG exports passed.
- In that browser build WebGL2 context creation was unavailable (environment restriction); its software 3D projection was rendered and captured. **GPU WebGL2 visual validation remains pending on a machine with a functioning graphics context.**
- Native vector blueprint produced from **actual exported WASM geometry**, not a hand-waved illustration. SVG parsed and rasterized.
- Reproducibility: `test_wasm.mjs` checks the exported geometry, signed sequence, clock closure, and wasm SHA-256.

## Build / reproduce

Compile with LLVM clang + wasm-ld installed:

```bash
clang --target=wasm32 -O3 -nostdlib -fno-builtin \
  -Wl,--no-entry -Wl,--export-all -Wl,--export-memory \
  -Wl,--initial-memory=262144 -Wl,--max-memory=16777216 \
  -o ket_io_core.wasm ket_io_core.c
node test_wasm.mjs
```

`KET_Generative_IO_3D_WASM.html` includes the **exact** compiled `ket_io_core.wasm` embedded as a Base64 string, with a fixed SHA-256 digest. To rebuild the self-contained HTML after changing C, replace the embedded Base64 and SHA-256; that would be a **new additive version**, not a modification of the frozen one.

## Frozen source of truth

- Original full kernel spec: `kernel/specifications/KET_TOROID_360_3_3_FULL_SPEC_v2_0_FROZEN.md`.
- Frozen kernel commit: [`de8f8b80aba3a73dd371811f6b4be39df92e45ce`](https://github.com/DavidWise01/oasis/commit/de8f8b80aba3a73dd371811f6b4be39df92e45ce).
- This application is an **adapter/viewer**, does not edit or retrain the immutable kernel, and contains no API calls, account access, or telemetry.

Scientific boundary: this is deterministic symbolic/control geometry. It does **not** establish the universe as a toroid, a Planck-scale mechanism, or a Sagittarius A* cipher. The 360 vs 366 count is a design convention, not 366 physical degrees.