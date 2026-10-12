# ALON / Single Force Carrier — independent operator

**Date:** 2026-10-12  
**Status:** interactive model-local configuration layer for the separate ALON materials lab. It is **not** a newly discovered nuclear interaction, actual particle collider, dye recipe or optical device.

## User rule (unchanged)

```text
{{ 1 :: force carrier :: { weak , medium strong }} :: 1 :: - or + :: 1 :: color :: 2 out of 8 :: }}}
```

The literal includes `}}}` as supplied. **Do not rebalance or change its spelling to make it executable.**

## Interpretation

```text
        ALON::single-carrier
                 |
          one carrier slot
                 |
           weak/medium/strong   [choose ONE]
                 |
             - or +            [choose ONE]
                 |
             colors            [choose TWO of EIGHT]
                 |
          select ALON lane     [A, L, O, N]
                 |
         observe toy pressure
                 |
           manual snapshot
```

The **force carrier**, **orientation**, and **color** headings each have one model register. The number two counts color selections, not force particles. The exact physics relation between such symbols and genuine Al–O–N solid-state bands is **not defined**.

Palette: `bk = black, wt = white, red, blu = blue, gree = green, yell = yellow, purpl = purple, orang = orange`. These are visual labels. The console initially displays black/orange but the user did **not** specify a forced active pair; either choice is editable.

**Mathematical only**: with unordered, nonrepeating pairs, `8 choose 2 = 28` pairs. Selecting one of three modes and one of two signs gives `3×2×28 = 168` possible *interface combinations*. None are new nuclear forces, count of atoms, allocated nodes or wave frequencies.

## Physics boundary

The **Standard Model** of particle physics distinguishes electromagnetic/photonic, weak/W/Z and strong/gluon interactions. A "medium force" is **not** a separately recognized interaction; treat weak/medium/strong as qualitative symbolic bands rather than named force-carrier bosons. Strong-interaction `color charge` is a gauge quantum number, not literally any of these visible palette swatches.

ALON chemistry remains approximate `Al₂₃O₂₇N₅` with its aluminum, oxygen and nitrogen atoms in a real cubic spinel material. The fourth `L` track describes structure/lattice, not a fourth element. The force register does not change the chemistry.

The console reuses the original **toy** curved spherical pressure-shell relation (`Δp r/(2t)`) and a simplified fracture-intensity approximation, via the unchanged `evaluateAlon` function. Changing the mode, sign or colors intentionally does **not** change these material calculations. There is no established pressure/polarization/color-control law.

## Launch

From the repository root:

```bash
python -m http.server 8000
```

Then open `http://localhost:8000/projects/xenonite-x0/alon-separate/force-carrier/`.

Or use a static hosted copy retaining the repository path structure. The browser loads `force-carrier.mjs` and imports `../alon-track.mjs`. Direct `file://` loading may be blocked by ES-module origin restrictions.

## Files

- [index.html](./index.html) — live mode, sign, two-color, lane controls and pressure response.
- [force-carrier.mjs](./force-carrier.mjs) — bounded, human-triggered operator state + manual snapshot ledger, at most 128 records.
- [force-manifest.json](./force-manifest.json) — identity, grammar and data limits.
- [Original ALON separate-tracks readme](../README.md) — physical material source ledger and pressure caveats.

**Original ALON source, Madre Sapphon and frozen KELVIN source remain unchanged.** No tests or physical synthesis were requested or performed; no claim of browser execution/validated material property is made.
