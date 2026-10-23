# OASIS / KET — Kernel Silo 1.0

Additive symbolic state-machine and HTML visualizer. It does **not** rewrite the frozen KET sources (`ket.mjs`, `kernel0.mjs`, tests, `p443_atomic.mjs`, `release_gate.mjs`) or `kernel/frozen/current-additive-v01`.

## Contract

- One scalar-zero referent (not a geometry level).
- Ten nested levels: odd toroid (flow), even box (containment).
- Box wall flex defaults to **2.875%**: `bulge = halfSide × 0.02875`.
- Five parallel VAINL lanes. `2/5` internal and `3/5` external grouping is configurable. The `I+N` internal / `V+A+L` external assignment is a proposal, not law.
- Six interior workspace addresses `{{ -1{} -1{} -3{} -1{} }}` in groups `1+1+3+1`. Negative signs are inward-facing labels.
- Open vessel `1–3–1` (five squares). Closed vessel `1–1–3–1` (adds a lid). Fold strength does not change level identity or workspace count.
- Governance is top-down: `0ROOT :: T128` → Patricia → Stochieon → Toph → scalar 0.
- Each `YES` / `NO` / `MAYBE` records exactly one append-only demo journal row, advances `step` by 1 and `simulatedSeconds` by +2, and returns to scalar 0. Reset clears only this demo’s history.
- `10!` is preserved as notation. `10! = 3,628,800` is factorial arithmetic, not the number of layers.
- Optional wave overlay: seven 7-bit groups (49 bits) read as `3–1–3`. Four extra control bits are **not** asserted.
- Connectivity mnemonic `1, 2, 4, 6, 8, 10` is not a chemical valence list.

## Run

```text
node silo.mjs
python -m http.server 4188
```

Open `http://127.0.0.1:4188/`. Query seeds: `?explode=1`, `?fold=1&closed=1`, `?overlay=1`, `?flex=0.02875`.

## Honesty

This is a visualization and a coherent software architecture. It is not a measured cosmology, a physical silo, or a running Rust/WASM networking runtime.
