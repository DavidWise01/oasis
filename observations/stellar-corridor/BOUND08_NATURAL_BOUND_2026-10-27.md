# Natural Bound 08 — Exact 24! toroidal traversal, 000 → 001 (2026-10-27)

Evidence ID: `ITD_BOUND08_24_FACTORIAL_TOROID_000_TO_001_20261027`

**State:** `CANONICAL_COMBINATORIAL_CYCLE_CONSTRUCTED` + `EXACT_BIGINT_RANKING` + `729_MODEL_STATIONS_PRESERVED` + `DIRECT_JUMP` + `REVERSIBLE_SINGLE_SWAP` + `CYCLIC_SEAM` + `OBSERVATIONAL_GATES_UNCHANGED`.

Append-only successor to [Natural Bound 07](BOUND07_NATURAL_BOUND_2026-10-27.md). This is the **computational traversal layer**, not an additional observational solution to Milky Way dynamics. No earlier physics, evidence CSV, or observational assumptions are rewritten.

## Canonical transition

```text
24 independent, distinguishable symbolic operator registers: [01 ... 24]
3-bit synchronized Gray register:                  000
729 prior radial numerical observation stations:   000 (center, g undefined)
                                     |
                                     |  +1 factorial rank
                                     |  exactly one adjacent operator swap
                                     |  one Gray bit changes
                                     v
RANK 1: [01 ... 22 24 23]                      GRAY 001
                                             STATION 001 (~11.37 pc from Sgr A*)

...
                                 ALL 24! STATES
                                 (lazy, exact rank access)
...
LAST RANK: 24!−1 = 620448401733239439359999
LAST SJT ORDER: [02 01 03 04 ... 24]
LAST GRAY: 100 ; LAST STATION: 728 (Sun)
                                     |
                                     |  +1 modulo 24!
                                     |  adjacent swap at slots 01,02
                                     |  Gray 100 -> 000, exactly one bit
                                     v
RANK 0: [01 02 03 04 ... 24]                GRAY 000 ; STATION 000
```

The final-to-initial rank is a **mathematically closed address seam**, **not** a physical Sun→Galactic-Center shortcut.

## Exact combinatorial construction

`24! = 620448401733239439360000` possible permutations of 24 distinct operators.

The code uses a recursively ranked Steinhaus–Johnson–Trotter (SJT) order, also known as plain changes. To unrank permutation `P_n(r)`:

```text
n >= 2
parent_rank = r // n
position_index = r mod n
P = P_(n−1)(parent_rank)

if parent_rank is even:
    insertion_position = (n−1) − position_index
else:
    insertion_position = position_index

insert symbol n at insertion_position in P
```

The reverse operation removes the largest symbol, recursively ranks the `n−1` permutation, and reconstructs the insertion direction and remainder. This gives exact random access and an inverse function, **not** a sequential enumerator. Each neighboring pair has one adjacent swap; the first and last also differ by an adjacent swap. The cyclic property is known in the combinatorial-generation literature:
https://wrap.warwick.ac.uk/id/eprint/174321/13/WRAP-combinatorial-generation-via-permutation-languages-acyclic-orientations-Mutze-2023.pdf

```text
Gray(k) = three_bit_binary( [k mod 8] XOR ([k mod 8] >> 1) )

000 → 001 → 011 → 010 → 110 → 111 → 101 → 100 → 000
```

Because `24!` is divisible by `8`, the synchronized Gray phase returns to 000 exactly at the permutation cycle seam. Every adjacent step changes precisely **one bit**, including the wrap.

The 729-station address is `station(k) = k mod 729`, not a power-law gravitational scaling. Since `729 = 3⁶` and `24!` contains `3¹⁰`, it divides exactly:

```text
24! / 729 = 851095201280163840000 exact logical visits per station
```

The 729 physical-model positions and numerical gravity values were copied unchanged from [Bound 04](SGRA_EARTH_729_MW_COMPONENTS_20261027.csv). Their source remains a **model** and does not become a survey simply by indexing it 24! times. Station `000` retains the originally undefined point-mass field at r=0.

## Visualization and interfaces

The standalone HTML [bound08-24factorial-toroid.html](bound08-24factorial-toroid.html) embeds the exact algorithm **and** all 729 prior gravity-model station values; no network requests or third-party scripts are required when its HTML bytes are locally available. The separate [bound08_toroidal_core.js](bound08_toroidal_core.js) is a reusable, dependency-free browser/Node module.

- Project 24 colored symbol lanes onto a visual 3D toroidal cross-section (8 red, 8 green, 8 blue; color names used symbolically).
- Show the exact current SJT permutation and highlight the swapped neighboring slots.
- Step +1 or −1, pause/play, jump to rank 24!−1, test last→first seam, reset to 000, or enter any valid **exact 24-digit** BigInt rank.
- Display three Gray bits, the 000–728 station register, station model radius, and all original `g_BH`, `g_bulge`, `g_disk`, `g_halo` and total inward acceleration values.
- Distinguish direct arbitrary index jumps from proved single-step swaps.
- Render an intentionally many-to-one 3D torus projection; it does **not** claim to embed 24! objects at distinct locations or realize a 24-dimensional physical manifold.

## Executed verifications and limits

1. Original `bound08_toroidal_core.js` retrieved after commit and **executed** in a JavaScript isolate.
2. Exhaustive rank/unrank uniqueness, adjacent-swap tests, and cyclic closure for *every permutation* of 2–8 symbols. Counts by n: `2!+3!+4!+5!+6!+7!+8! = 46,232` enumerated test cases. This does not enumerate 24!.
3. **610** exact sampled 24! BigInt ranks, including first, second, last, penultimate, midpoint, boundaries and deterministic pseudorandom addresses: roundtrip, adjacent permutation, Gray step and station number all passed.
4. Exact algebraic checks: `24!`, `24!/729`, Gray period, station 000→001, and last Gray 100→first Gray 000.
5. Both inline scripts from committed HTML were separately checked for valid JavaScript syntax. The active controls were additionally exercised using a lightweight mock DOM: initial 000, step +1→001, last state, last→first seam, reverse seam, exact BigInt jump, reject out-of-range input. All passed.
6. Model field snapshot has **729** entries. Station 000 has null physical-model values, station 001 has radius ~11.3695 pc and total field ~1.831898e−8 m/s², station 728 has radius 8277 pc and total field ~2.125633e−10 m/s². Those are **prior model outputs**, not independent astronomical readings.
7. These tests **do not** constitute a full Chromium screenshot/render evaluation or independent confirmation that GitHub Pages is serving the new file. The repository API reports `has_pages=true`, but the new path was not live-verified.

## Physical containment

This 24! toroidal transversal is a **logical state address construction**, mathematically valid as a permutation Gray-cycle independent of astrophysical matter. It does not define the global topology of Milky Way space, convert sampled stars into gravitational transmitters, demonstrate new gravitational law, or address the unresolved Eilers/Gaia/H I tracer discrepancies. Toroidal geometry is a *chosen visualization*, not a discovery of a physical torus.

The 729 station model retains its caveats, including calibration at the Sun, inner-Galaxy residuals, and potential bar/spiral asymmetry. There is no physical causal coupling between the rank permutation and local gravity values, and none is implemented.

## Git files

- [Standalone interactive viewer](bound08-24factorial-toroid.html)
- [Pure reversible 24! engine](bound08_toroidal_core.js)
- [Machine-readable audit and all guardrails](BOUND08_TRAVERSAL_AUDIT_20261027.json)
- [Prior physical Bound 07](BOUND07_NATURAL_BOUND_2026-10-27.md)

## Next natural Bound 09

Build a **true time-ordered gravitational observation register** instead of mapping a symbolic permutation directly to physical motion: attach measured 6D stellar phase-space vectors (Galactic position plus velocity, including covariance) to valid observational stations, keep unmeasured stations empty, and compare the bar/spiral `m=2` kinematic residuals without re-fitting a held-out dataset. The toroidal index may be used as a deterministic view selector or replay-address mechanism, but its counter must not be confused with physical time. Independent stellar dynamical validation would require solving orbital equations in a published potential and checking survey selection effects.
