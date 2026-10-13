# KET Generative I/O — Six Signed Directions, 3D WASM v0.5

**2026-10-13 · Additive correction to the v0.4 spatial selector; frozen KET v2.0 unaffected.**

User: **“since time is linear its only x,y,z or ---0+++ six axises only”**

## Corrected vector rule

There are **three spatial axes**, X/Y/Z, with two signed directions each (**six signed rays**), plus origin `0`: **seven permitted placements per toroid**, **49 ordered placement pairs** of two independent toroids. Previous v0.4's `3³=27` per toroid and `729` placement pairs were an overly broad assistant interpretation, and are superseded.

| Code | Place | XYZ |
|---:|---|---|
| 0 | origin | (0,0,0) |
| 1 | −X | (−1,0,0) |
| 2 | +X | (+1,0,0) |
| 3 | −Y | (0,−1,0) |
| 4 | +Y | (0,+1,0) |
| 5 | −Z | (0,0,−1) |
| 6 | +Z | (0,0,+1) |

WASM low-level `set_vectors` rejects all diagonal selections through the condition `abs(x)+abs(y)+abs(z) <= 1`, where each component is −1/0/+1. The new exported `set_directions(A,B)` and `get_direction(torus)` provide directly validated seven-code selection. The **linear time** reference is the sequential integer simulation tick, **not a fourth selectable spatial coordinate or a claim about fundamental spacetime**.

## Frozen KET and Rules 01–02

Each toroid is still an independent KET instance with `20×18=360` surface ports and `3+3` controls: **366 logical addresses each**. Neither a vector direction nor a derived radial cell allocates kernel addresses. Rule 01: six mnemonic boundary positions plus one **permanent open through-hole**, not a seventh wall or an outer box. Rule 02: independent optional data-gate modes OFF/A→B/B→A/BOTH with independently selected communication port 0..359, even if the body centers coincide.

WASM cell state is a deterministic synchronous cellular automaton (ready, excited, refractory), seeded and updated on each tick. The `--+ ++-` then `++- --+` schedule completes a baseline 360° cycle in 360 ticks, and both tori separately recover speed. The Chariot `123 {{45/|\54}} 678`, two separate Green slots, seven ordered amplitudes, three carriers, and pinned zero are preserved.

## Files

- `index.html` — completely offline standalone HTML with compiled WASM embedded; user can open it in a modern browser.
- `src/vector_toroid.c` — compilable no-import `wasm32` source; includes strict six-direction validation.
- `index.template.html` — source of the fully offline UI; **two seven-option menus** replace six axis dropdowns.
- `build.py` — compiles the offline page from `vector_toroid.wasm` and template; build requires clang/wasm-ld externally.
- Companion conversation ZIP includes exact compiled `vector_toroid.wasm`, local full `test_six_axis.mjs` (54 assertions), browser QA, real WASM positions rendered into an editable **3200×1800 SVG**, PNG, JSON/CSV receipt and SHA256 manifest. The ZIP is **not claimed to be stored in this repository**.

Build from the source:

```sh
clang --target=wasm32 -O3 -nostdlib -fno-builtin \
  -Wl,--no-entry -Wl,--export-all -Wl,--export-memory \
  -Wl,--initial-memory=393216 -Wl,--max-memory=16777216 \
  -o vector_toroid.wasm src/vector_toroid.c
python build.py
node test_six_axis.mjs
```

## Verification

- Local release: **54/54 WASM checks**, including all **49 placement pairs**, diagonal rejection, independent controller and cellular states, directional message permissions, shared zero without forced merge, 360-tick closure, deterministic replay.
- Chromium: two ray selectors, A→B delivery, gate OFF zero messages even with identical origin, full circuit and JSON/CSV/PNG exports passed, no JS exceptions.
- WebGL2 GPU hardware rendering has **not** been validated in this test environment. The Canvas2D **software projection of WASM-generated 3D coordinates** was exercised.
- Release compiled WASM SHA-256: `8bfcd05932d366497174c063b98411f044f4253b69ce6969e495ae1f75c16d7c`. A fresh rebuild should verify its own binary digest; compiler and source provenance matter.
- This is a programmable symbolic geometry, **not** verified Planck-scale or cosmological physics.

**Authoritative policy:** [Rule 03 — Six Signed Spatial Directions](../../architecture/KET_RULE_03_SIX_SIGNED_AXES_LINEAR_TIME_20261013.md) · [Frozen v2.0](https://github.com/DavidWise01/oasis/commit/de8f8b80aba3a73dd371811f6b4be39df92e45ce).
