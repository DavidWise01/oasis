# KET Rule 03 — Six signed spatial directions and a separate linear time counter

**Date:** 2026-10-13  
**Status:** User-corrected authoritative spatial occupancy interpretation. Supersedes v0.4's 27-point Cartesian-product reading of `0.-+.`. **Frozen KET v2.0 unchanged.**

> since time is linear its only x,y,z or ---0+++ six axises only

## Exact position contract

The 3D coordinate frame is exactly **X, Y, Z**. Each independent KET toroid may occupy one of these **six signed directions**, plus the shared coordinate origin **0**. Thus `---0+++` is read as **three negative directions, origin, three positive directions**, not a fourth spatial/time axis and not the unrestricted `{-1,0,+1}^3` Cartesian product.

| Direction | Code | X | Y | Z |
| --- | ---: | ---: | ---: | ---: |
| origin | 0 | 0 | 0 | 0 |
| −X | 1 | −1 | 0 | 0 |
| +X | 2 | +1 | 0 | 0 |
| −Y | 3 | 0 | −1 | 0 |
| +Y | 4 | 0 | +1 | 0 |
| −Z | 5 | 0 | 0 | −1 |
| +Z | 6 | 0 | 0 | +1 |

```text
           - - -   0   + + +
           -X -Y -Z  O  +X +Y +Z

 spatial axes: X, Y, Z
 allowed placements / toroid: 6 oriented rays + 0 = 7
 ordered placements / twin toroids: 7 × 7 = 49
 forbidden: diagonal/composite signed placements,
            e.g. (+1,+1,0), (+1,0,-1), (-1,-1,-1)
 chronological step t: 0,1,2,... (not an extra spatial axis)
```

**Alternative low-level criterion:** each component must be one of -1,0,+1 and the L1 norm `|x|+|y|+|z| ≤ 1`.

Each toroid owns its individual identity, open toroidal through-hole (Rule 01), cellular state, 366-address frozen register and optional information gate (Rule 02). A may select any permitted position independently of B; both can occupy 0 simultaneously without forced merge or exchange. Their selected centers are `spacing × signed_unit_direction`. Gap distance is a geometric diagnostic; it is not a permission flag. Each toroid progresses via an ordered simulation tick counter, independently of spatial movement. Do not reinterpret this as a cosmological statement about the nature of time.

## Forward WASM build and proof

Implement in additive **3D WASM v0.5** (not edits to frozen KET or the historical v0.4 release). Remove six independently adjustable dropdowns; replace them with one seven-position direction selector per toroid. WASM must independently reject diagonal placement even when invoked without the UI. Retain Rule 01's `4+3=6+hole`, all optional messaging directions, the Green Chariot `123 {{45/|\54}} 678`, seven ordered amplitudes (Green twice), three carriers, and the frozen `360+3+3=366` address accounting.

Companion ZIP **KET_Generative_IO_SixAxis_3D_WASM_v05.zip**: real compiled wasm32 cellular-state and position generator, self-contained offline HTML (real WebGL2 path with software 3D fallback), recompilable C source, Node assertions, Chromium interactions/exports, native 3D blueprint and SHA256 manifest.

**Locally executed:** **54/54 WASM checks PASS**; Chromium startup, two distinct signed rays, directed A→B message, shared origin/OFF zero transfers, 360 tick closure, JSON/CSV/PNG exports PASS with no browser JavaScript errors. Hardware GPU WebGL2 visual validation **remains pending**. Physical Planck-scale claims are not made.

## Frozen reference

KET v2.0 pinned Git commit: `de8f8b80aba3a73dd371811f6b4be39df92e45ce`. Its bytes remain invariant. The prior Rule 03 v0.4 implementation remains in Git history as a superseded interpretation for auditability.
