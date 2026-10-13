# A.I.O.N. v1.5 — Additive K.E.T. execution adapter

**Status:** working local integration of two existing executable modules; **not a modification of the frozen OASIS/K.E.T. runtime** and not certified physical device modeling.

The adapter implements the three OASIS control tracks as an application-level interface:

- `K / i` — check SHA-256 source fingerprints, restrict mode, validate the reference crystal.
- `E / u` — invoke the actual `buildAlonCrystal()` Node.js module and/or original `aion_v14.py` synthetic pulse spectroscopy engine in an isolated directory. Check that generated structure and outputs meet their invariants.
- `T / u.s` — export content hashes, a JSON execution receipt, and an append-only hash-chain event ledger. Identical reruns generate the same event and do **not** append duplicate ledger rows. A modified old receipt is rejected by the verifier before the next append.

The symbolic frozen K.E.T. kernel spec remains unchanged. The adapter is *aligned to*, not *executed inside*, its production source. No native OASIS production WAL, signed provenance, authentication, protection against privileged deletion, hardware verification, or official production-gate acceptance is claimed.

## Installation

Requires Python 3.10+ with `numpy`, `scipy`, and Node.js 18+.

Unzip and execute from the package directory:

```bash
python ket_aion.py --module all --out ./run-aion
```

Output paths must be outside the integration source directory. Supported module choices are `crystal`, `pulse`, or `all`.

When copied under `projects/xenonite-x0/alon-separate/ket-aion-runtime/` in OASIS, the Node bridge prefers the repository's existing `projects/xenonite-x0/alon-separate/material-build/alon-crystal.mjs` directly, instead of the bundled source-compatible snapshot. The snapshot is used only if that GitHub path is unavailable (e.g., in this standalone ZIP). Hashes record which source was actually selected.

Outputs for `all`:

- `alon-cell.json`, `alon-cell.cif`, `alon-cell.xyz` — 55-atom, 122-contact, 42-boundary crystal reference.
- `aion-v14-results.json`, `aion-v14-synthetic-pulses.csv`, `aion-v14-fit-ranking.csv`, `aion-v14-model-predictions.csv` — v1.4 original experiment, not reimplemented.
- `ket-aion-receipt.json`, `ket-aion-ledger.jsonl` — module source hashes and ordered execution event receipt.

The `alon-reference.json` is the existing reference model from the original ALON construction artifact; it is used for site/bond equality checks. No iodine is introduced.

## Executed integration validation

`python ket_aion.py --module all` yielded:

- 55 occupied sites, 122 nearest-neighbor contacts, 42 periodic boundary edges, formal charge 0.
- 700 synthetic v1.4 charge-recovery observations, 15 fitted models, 5 protocols.
- 11 in-run structure/readout assertions passing, plus replay and ledger-integrity checks.
- Identical rerun matched output hashes and preserved **one ledger record**.
- Intentionally corrupted ledger row produced `QUARANTINED` and an error exit.
- Separate `crystal` and `pulse` CLI modes successfully executed.

This is **synthetic model interoperability**, not evidence that the ALON crystal has been physically fabricated or behaves as a transistor.

## Integration / freeze boundary

Repository placement:

```text
projects/xenonite-x0/alon-separate/
├── material-build/
│   └── alon-crystal.mjs          # original source retained, never overwritten
└── ket-aion-runtime/            # additive runtime
    ├── ket_aion.py
    ├── crystal/{bridge.mjs,alon-crystal.mjs,alon-reference.json}
    ├── pulse/aion_v14.py
    └── README.md
```

The local adapter does not patch the immutable files in `kernel/production/` or make GitHub updates. It may be introduced as a new repository folder after review. To avoid accidental mutation of the production kernel, stage the folder on a review branch first.

## Scientific caution

ALON is an insulating ceramic. The pulse engine measures synthetic *normalized release charge* from assumed fast/slow traps, not electronic conduction through all 55 crystal sites, not a self-consistent atomistic quantum-transport simulation, and not observed ALON/Si interface kinetics. Its outputs should remain quarantined from physically verified material claims.

## 3D Canvas

Open `aion-3d-canvas.html` in a browser for offline, dependency-free 3D visualization of the 55-atom reference or 2×2×2 supercell. The model is embedded from the deterministic unrelaxed ALON reference. Drag to orbit, scroll to zoom, toggle species/periodic edges and save PNG. `aion-3d-blueprint.svg` is the professional vector engineering-sheet companion.

