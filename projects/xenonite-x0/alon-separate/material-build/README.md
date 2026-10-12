# ALON v2 — an actual computational crystal build

**Date:** 2026-10-12 | **Type:** inspectable, deterministic, bounded atomistic geometry + CIF/XYZ export.  
**Not:** a synthesized transparent ceramic, an experimentally measured microstructure, an optimized DFT model, a pressure-vessel certification, a nuclear-force simulation, or an alternative to the real ALON material already manufactured by Surmet.

## What was built

An idealized, periodized cubic defect-spinel 56-site **conventional cell** with the realistic ALON representative occupancy:

- `Al23 O27 N5` is a 55-atom population, plus one **vacant** cation site.
- Eight tetrahedral cation sites (8a): Al in all eight.
- Sixteen octahedral cation sites (16d): Al in fifteen, **one explicit vacant site**.
- Thirty-two anion sites (32e): 27 O plus 5 substituted N.
- Charge arithmetic under nominal formal oxidation states: `23(3+) + 27(2−) + 5(3−) = 0`.
- Reference cubic cell parameter **a=7.95 Å** and simplified anion internal coordinate **u≈0.260**, both adjustable only as indicated below.
- Calculated nominal density ≈ `3.710 g/cm³` using SI/CODATA Avogadro constant and atomic masses, not a measurement.
- A deterministic set of nitrogen positions indexed by seed 42, and configurable vacancy among 16 octahedral sites; **not experimentally refined** or energetically minimized.
- Pairwise cation–anion nearest-neighbor calculation using periodic minimum-image distances (for a=7.95 Å and a 2.25 Å cutoff: 122 bonds after the octahedral vacancy). Tetrahedral and octahedral Al sites are distinct.
- The individual explicitly N-substituted and vacancy-ordered snapshot exports as **P1**, not as full **Fd-3m**: the average ideal spinel can have Fd-3m symmetry but one chosen snapshot may not.
- [Example seed-42 CIF](./examples/ALON-Al23O27N5-seed42.cif), [XYZ](./examples/ALON-Al23O27N5-seed42.xyz) and [summary](./examples/alon-seed42-summary.json), created with fixed deterministic occupancy.

### Actual atom model vs interface lettering

```text
{{ -AaaA....LllL....OooO....NnnN.... }}
  AaaA = 23 Al atoms, 8 tetra + 15 octa
  LllL = 56 ideal spinel lattice positions with 1 vacancy
  OooO = 27 O atoms, 32 anion positions total
  NnnN =  5 N atoms substituted for O
           ----------------------------
           55 actual atoms + 1 vacancy

{{ 1 :: force carrier :: { weak , medium strong }} :: 1 :: - or + :: 1 :: color :: 2 out of 8 :: }}}
  one symbolic carrier | 3 modes | ± | two distinct colors of eight

  IMPORTANT: modes, signs and visible colors do NOT produce
             any real elementary-particle forces in this code.
```

## Use it

Host the repository directory with a simple static HTTP server:

```shell
python -m http.server 8000
```

Open:

```text
http://localhost:8000/projects/xenonite-x0/alon-separate/material-build/
```

Drag the cube to rotate. Change the seed (anionic nitrogen arrangement) or the octahedral vacancy index, select a chemical/structural track, change lattice parameter within 7.60–8.30 Å, and see the occupancies, formal charge, stoichiometry, density and nearest-neighbor bond links recalculate. Pressure/crack inputs use the **existing** simplified spherical-shell inspector and are kept completely separate from atomistic interactions.

Download:

- **CIF**: 55 actual atom sites + cubic unit cell + P1 space group; the vacancy is absent from `atom_site` entries and preserved in JSON.
- **XYZ**: 55 Cartesian-coordinate atoms, for viewers; standard XYZ does not reliably encode periodic cell geometry.
- **JSON**: full 56-site scaffold, occupied/vacant roles, input settings, bond distances, nominal density and explicit limitations.

The archived example is not a material database entry or a diffraction-resolved structure: N and vacancy ordering were chosen by deterministic pseudorandom assignment **only**, not by experiment or density-functional energy minimization. Molecular-dynamics or DFT researchers should relax candidate cells before making energies, elastic constants or electronic/optical predictions.

## Physical-science provenance

- **Weingarten & Byrd (2015)**, [_Special quasirandom structures of alon_](https://doi.org/10.1016/j.commatsci.2014.09.021): ideal Al₂₃O₂₇N₅ defect-spinel stoichiometry, disorder and vacancy, lattice ~7.95 Å, average space group Fd-3m; SQS methods explicitly necessary to approximate disorder.
- **NASA Glenn (2017)** [_Crack Growth Testing of an Aluminum Oxynitride_](https://ntrs.nasa.gov/api/citations/20170001289/downloads/20170001289.pdf): real ceramic mechanical specimen data, separate from modeled atomistic geometry.
- [Earlier ALON review](../../MATERIAL-ALON-CANDIDATE.md): sampled modulus, fracture toughness, true material limits and need for hermetic-seal qualification.
- Coordinate conventions are a **representative ideal Fd-3m origin choice 2 spinel 8a/16d/32e arrangement**; u=0.260 is a declared modeling approximation, not a fitted site parameter. No direct claim that an individual arbitrary N/vacancy assignment is experimentally stable.

## Independence

This module imports `../alon-track.mjs` to reuse the illustrative pressure equation and `../force-carrier/force-carrier.mjs` only for the separate palette constants. It **does not modify** either, or the Au79/Madre Sapphon model, or the frozen KELVIN source. No autonomous timers, background services, gene functions, generation recursion, hidden file persistence or external network calls.

**Structural invariants checked for the seed-42 example:** 8+16+32 sites, 23+27+5+1 occupancy, formal charge zero, 122 reference local bonds, nominal density ~3.710 g/cm³. This is model consistency verification, **not materials lab testing or proof of practical Xenonite**.
