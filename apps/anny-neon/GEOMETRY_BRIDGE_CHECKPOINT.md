# Anny Sapphon Radiation Geometry Bridge — Checkpoint

**Scope:** `apps/anny-neon/` on `main`, presentation-only.  
**Date:** 2026-10-21.

## Implemented

- `sapphon-geometry.mjs` is a pure registry-to-geometry projection plus a browser presentation mount.
- Reads radiation selection from the existing overlay's `data-active` attribute using a `MutationObserver`.
- Displays Gamma and X-ray together on the conceptual short-wavelength **photon context**, adjacent to the violet/UV end. Their energies can overlap. No gamma/X-ray numeric cutoff is asserted.
- Displays alpha and beta on a separate **particle axis**, with alpha physical charge `+2e` and beta `−e/+e` as appropriate to decay sign; these charges are not the Sapphon symbolic polarity.
- Lets the viewer select any of seven signed `−/+ ` Sapphon bands to inspect the two Greek epithets, short/long approximate nm endpoints, and original read-only cubit slot labels.
- Preserves the White broadband pair and non-spectral `-- VOID` / `++ GRAVITY` frame.
- Integrates HTML and responsive CSS into the GitHub Pages path.

## Invariants and testing

- `sapphon-geometry.test.mjs` adds **9 deterministic pure-model tests**.
- An isolated JavaScript V8 harness executed the committed `sapphon-spectrum.test.mjs` (7), `radiation-overlay.test.mjs` (5), and `sapphon-geometry.test.mjs` (9) against the corresponding committed source: **21/21 passed, zero failures**.
- A separate fetched GitHub source integrity audit passed **12/12 checks**.
- Actual `node --test *.test.mjs` execution, Chromium interaction testing, process-restart, and power-loss durability verification **were not performed** in this checkpoint.

## Non-authority boundary

The geometry module does not import the journal or receiver and does not access IndexedDB, transfer IDs, ACKs, or commit phases. It cannot issue delivery authorization. Gamma/X-ray and alpha/beta are physically distinct categories; the diagram is an observational, symbolic projection rather than evidence for a force coupling.

## Reproduce in a cloned checkout

```bash
cd apps/anny-neon
node --test sapphon-spectrum.test.mjs radiation-overlay.test.mjs sapphon-geometry.test.mjs
```

Open the Pages path at `/apps/anny-neon/` and toggle radiation types to inspect the geometry in a browser.
