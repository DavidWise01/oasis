# KET — Cellular Generative I/O, 3D WebAssembly v0.2

**Status:** executed / additive application layer. **Frozen KET v2.0 remains unchanged** and pinned to Git commit [`de8f8b80aba3a73dd371811f6b4be39df92e45ce`](https://github.com/DavidWise01/oasis/commit/de8f8b80aba3a73dd371811f6b4be39df92e45ce).

Open **`index.html`** (or `KET_Cellular_Generative_IO_3D_WASM.html`) in a modern browser. It is fully offline/self-contained, embeds a genuine compiled `wasm32` binary, and does not load libraries or use a network. WebGL2 is the primary 3D point-field rasterizer; interactive Canvas2D projected 3D from the **same WASM-generated 3D coordinates** is the fallback.

## Frozen kernel boundary / no mutation

```text
                         KET :: FROZEN v2.0
                       immutable Git commit pin
                                  |
           20 skins x 18 sectors = 360 surface address ports
                                  |
       6 control addresses = --+ and ++- (existing CATGNO slots)
                                  |
          360 + 3 + 3 = 366 immutable logical addresses
                                  |
                        READ-ONLY WASM ADAPTER
                                  |
       360 base ports x 1..6 ephemeral radial layers = 360..2160
                                  |
          local derived cellular states {-1,0,+1} @ 1 pp/cell
                                  |
             LIVE 3D I/O / CA, replay and receipts
```

The **additional cellular states are transient runtime data**: they are **not new kernel cubits, not a reallocation of 366 addresses, and not a new physical Planck-scale claim**. The toroidal 20×18 surface can be read as four 10×9 local tiles with up to 6 depths each, retaining a local maximum of **10×9×6 = 540** derived cells per tile (less than the user-established 10³ local tensor limit).

The literal Green Chariot is unchanged: `123 {{45/|\54}} 678`, with distinct Green IDs A2 and A6 in the seven **ordered** color amplitudes `R G B O P G Y`. The three carriers remain white, black and gray; zero pinned. Five named operators and the LIFE ENGINE are untouched.

## What is generative?

The WASM core maintains a per-cell synchronous, discrete, 3-state cellular automaton **inside a toroidal volume**, not merely colored graphics. A seeded initialization produces actual live cells; each clock tick reads neighbor states and updates cell state and age. It can remain active for hundreds of generations. It is **not a cellular model of fundamental physics**.

Let state `x ∈ {-1,0,+1}` mean:

| Code | Name | Rule on next generation |
|---|---|---|
| +1 | excited | becomes −1 (refractory) |
| −1 | refractory | becomes 0 (ready) |
| 0 | ready | becomes +1 if enough excited neighbors or if a reproducible sparse seed gate fires; else remains 0 |

Every cell has **up to six immediate neighbors**: ± one toroidal-major angle, ± one toroidal-minor angle, ± one radial depth. The two angular coordinates wrap periodically. The radial boundary does **not** wrap, so extreme radial layers have fewer neighbors. All state transitions are synchronous; the next-state buffer is committed only after the entire previous generation has been read.

`T_eff = max(1, threshold + (control < 0 ? 1 : control > 0 ? -1 : 0))` is the local threshold: slow sign inhibits excitation, fast sign favors it. The seed gate uses an integer hash of `(seed, cell index, generation)` with chance parameter `pulse` per thousand. The seeded gate is purely **pseudorandom, deterministic**; its 1/1000 controls are app-level parameters, **not** scientific physical decay rates or immutable KET constants.

### Frozen toroidal speed controller preserved

The frozen order is `--+ ++-` in the first 6 ticks, then `++- --+` using the **same six control addresses** in the next six ticks, followed by 348 neutral ticks:

```text
  ω[k+1] = ω[k] + δ · s[k]
  θ[k+1] = θ[k] + ω[k+1]
  s[k]   ∈ {−1,0,+1}
  ω0     = 1°/tick (illustrative)
  δ      = 0.1°/tick (illustrative)
  θ[6]   = 5.7°
  θ[12]  = 12.0°
  θ[360] = 360.0°
  ω[360] = 1.0°/tick
```

That **angular** 360° is not the count of 366 *logical addresses*. The cellular states at generations 0 and 360 are generally *not equal*; closure applies to the controller's rate/phase, not to every emergent cell. A new 360-tick cycle starts without reseeding until the user presses Reset or Generate.

## Inputs / outputs

Users can change 1–6 layers, excitation frequency in per-mille, neighbor threshold 1–5, reproducible 32-bit seed, generation rate, and torus major/tube radii. The WebGL2 and Canvas2D interactive viewers both provide pointer orbit and zoom; clicking selects a cell to inspect a 7×7 neighborhood at its radial depth.

Controls: **Generate**, **Play/Pause**, **Step**, **+12 gate**, **360 circuit**, **Reset**. Export **JSON receipt** (input, frozen register, WASM SHA, state checksum and every observed generation), **CSV trace**, and **PNG viewport**. No network calls, remote telemetry, automatic GitHub writes, or production append-only ledger mutations.

The running FNV-1a checksum is a **non-cryptographic** state integrity value. The bundled source and release manifest use separate true SHA-256 hashes. Two simulations with identical seed, parameters and tick counts reproduce identical state and geometry.

## Execution and QA (2026-10-13)

- Actual C compiled to self-contained no-import **WebAssembly** (`ket_cellular.wasm`). The exact binary is Base64-embedded in `index.html` alongside its SHA-256.
- **23/23** independent WASM assertions (`node test_wasm.mjs`) cover WASM validation/imports, layout and state code, 360° / 360-tick closure, seed and state-hash replay, boundary validation, max/min cellular layers, and positive population after 360 generations.
- Default seed 42, 3 radial layers, threshold 2 and excitation 45 per-mille: **88 excited cells after generation 360**, deterministic on rerun. It is a demonstrated sample, not a scientific prediction.
- Chromium DOM/browser tests: initialized embedded WASM without JavaScript exceptions; controls 12-step + 360-step, reset, edited five-layer 1,800-cell generation and 84 subsequent steps, exact Chariot export, JSON/CSV/PNG downloads passed.
- Chromium's WebGL2 context was **unavailable in this environment** (including software GPU configurations); the Canvas2D interactive 3D fallback was rendered and screenshot-tested. Do not claim visual GPU shader validation on hardware. WebGL2 shader/point renderer is implemented, **hardware GPU QA remains pending**.
- Editable `CELLULAR_WASM_3D_BLUEPRINT.svg` is **3200×1800 native SVG**, derived from actual WASM cell positions/states at generation 84 and independently parsed/rendered to PNG.
- Frozen controller source, checksum manifest and Git history were not changed. This repo subdirectory is a new **additive v0.2 application version**.

## Rebuild

Requires clang/wasm-ld and Node.js. Running the app needs neither.

```bash
clang --target=wasm32 -O3 -nostdlib -fno-builtin \
  -Wl,--no-entry -Wl,--export-all -Wl,--export-memory \
  -Wl,--initial-memory=393216 -Wl,--max-memory=16777216 \
  -o ket_cellular.wasm src/ket_cellular.c
node test_wasm.mjs
python build.py                # inserts wasm base64 / digest in standalone HTML
python render_blueprint.py     # uses snapshot_gen84.json
```

If changing code or rules, make an **additive v0.3**, not a mutation of frozen KET v2.0.

## Scientific status

Here, **Planck-point (pp)** is a user-defined symbolic address and microscope-scale *analogy*. No code models actual Planck length, Planck time, quantum gravity, cosmology, proton properties, or microphysical stellar dynamics. There is no physical evidence that the universe follows this cellular update law. Mathematical reproducibility is not physical verification.
