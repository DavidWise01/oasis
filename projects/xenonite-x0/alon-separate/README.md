# ALON — four separate symbolic tracks

**Date:** 2026-10-12  
**Project:** `projects/xenonite-x0/alon-separate/`  
**Status:** independent live/manual material-study companion. **No modifications to the frozen KELVIN 11.3 or the Aa.Nn.Nn Madre Sapphon vessel.**

## Exact user inscription

```text
{{ -AaaA....LllL....OooO....NnnN.... }}
```

Preserve:
- Outer `{{ ... }}` closure, **single leading minus** before `AaaA`, exact case.
- Four motifs each comprising **4 characters**: `AaaA`, `LllL`, `OooO`, `NnnN`.
- Four literal **four-dot** runs `....` between each segment and after `NnnN`, **16 dots total**. No role (time, distance, natural decay or quantum leap) is assigned to the dots without further user instruction.
- **Exactly four separately selectable symbolic lanes.** The sign is a structural orientation, not a negative electric charge, dangerous chemistry or minus-one atom count.

## Chemical grounding — do not turn the glyph into a formula

| Separate lane | Provisional observed material layer | Actual elemental identity | Approximate formula-unit count |
|---|---|---|---:|
| `AaaA` | aluminum component | Al, atomic number 13 | 23 |
| `LllL` | connected solid-state lattice and crystallographic defects | **None: L is NOT an element** | n/a |
| `OooO` | oxygen component | O, atomic number 8 | 27 |
| `NnnN` | nitrogen component | N, atomic number 7 | 5 |

**ALON** stands for aluminum oxynitride, a real optically transparent polycrystalline cubic-defect-spinel ceramic. `Al₂₃O₂₇N₅` is a **representative approximate composition**, not a fixed molecular unit or guarantee of exactly 55 lattice sites. Stoichiometry, vacancies, atomic ordering, grain boundaries, surface flaws and residual stresses vary.

The UI's 55 dots are **count tokens** from the approximate ratio `23 + 27 + 5 = 55` placed in arbitrary 11×5 visual rows. They are **NOT** crystallographic coordinates, a computed unit cell, an elemental periodic table or 55 independent quantum processors.

## Separate single-carrier operator (live companion)

A **new, separately runnable** [force-carrier lab](./force-carrier/) is connected to the original four ALON material lanes. It preserves the user's rule **exactly**, including the extra closing bracket:

```text
{{ 1 :: force carrier :: { weak , medium strong }} :: 1 :: - or + :: 1 :: color :: 2 out of 8 :: }}}
```

- **One carrier** register, with **one active weak / medium / strong mode**. These are symbolic intensity tags; established physics does **not** contain a separate "medium nuclear force."
- **One** sign selected from `-` or `+`, independent of the first minus in the original ALON inscription.
- **One** color register selecting **two DISTINCT palette entries from eight**: `bk/wt/red/blu/gree/yell/purpl/orang`. Initial black and orange selection is provisional, not user-mandated.
- One of the four already defined ALON lanes (`AaaA/LllL/OooO/NnnN`) is the active visualization focus, with unchanged real chemistry `Al/O/N`.
- Selecting colors does not specify optical wavelengths or the technical red/green/blue gauge-color charges of the nuclear strong force. No physical force-carrier coupling to materials is assumed.
- `C(8,2)=28` unordered color pairs; `3×2×28=168` mathematical possible mode/sign/pair selections. They are **options**, not 168 physical particles or nodes.
- All current selections change on operator input. Each record is appended only on an **explicit snapshot click**, capped at 128 with manual JSON export. The force overlay imports `evaluateAlon` for the existing illustrative engineering readout; it does not modify `alon-track.mjs` or the KELVIN engine.

For code and scientific caveats see [force-carrier/README.md](./force-carrier/README.md).

## Executable ALON v2 unit-cell construction

[Open the **material crystal builder**](./material-build/) to generate a nominal Al₂₃O₂₇N₅ spinel occupancy model: 8 tetrahedral Al positions, 16 octahedral Al positions (one vacancy), and 32 O/N positions (27 oxygen and 5 nitrogen). The code includes drag rotation, deterministic nitrogen substitution and vacancy selection, nominal mass/density/charge calculations, and actual downloadable **P1 CIF, XYZ, and JSON** coordinate files. It imports the unchanged force palette and the existing ALON engineering example, but never derives new physical forces. [Sources and scope](./material-build/README.md).

## Run the live inspector

Serve the repository root over HTTP:

```shell
python -m http.server 8000
```

Open:

```text
http://localhost:8000/projects/xenonite-x0/alon-separate/
```

The HTML uses a relative ES module import. It may not load through a direct `file://` URL. There is no npm install, no remote APIs, network telemetry, autosave, autonomous agents or physical interface.

## User actions

1. Click **AaaA, LllL, OooO or NnnN** to focus the separate symbolic track. This selects a material-view overlay only; chemical atom populations stay 23/27/5.
2. Edit inside/outside **absolute atmospheres**, radius, shell thickness, hypothetical crack half-length, LEFM geometric factor `Y`, passive attenuation rate `κ` and propagation length.
3. Read the **idealized** spherical membrane stress, `K_I`-like stress intensity, ratio to **a particular NASA test specimen's** reported toughness, and optional signal attenuation.
4. Click **Append selected track snapshot** to commit a single in-memory record. There is no autonomous progression. Maximum 128 operator-triggered snapshots, **separate from** the canonical KELVIN's 128 manual turns.
5. Click **Export JSON ledger** to save the append-only session. Browser reload loses the in-memory records.

## Models and known limits

```text
Δp = (p_inside_atm - p_outside_atm) × 101325 Pa

IF Δp > 0:
   spherical σ [MPa] = (Δp × radius_m)/(2 × wall_m) / 1e6
   K_I [MPa√m]      = Y × σ [MPa] × √(π × a_m)
   fracture ratio   = K_I / 2.19 MPa√m
ELSE:
   external-pressure buckling/collapse not evaluated
   tensile σ and K_I not evaluated

R / R0 = exp(-κ × path_m)
```

`K_I = Yσ√(πa)` is a **simple linear-elastic mode-I fracture approximation** assuming a uniform tensile stress and a suitable crack-shape correction. The NASA `K_IC ≈ 2.19 MPa√m` value is a **measured property of specific tested ALON specimens in dry nitrogen**, not an allowable stress or one universal future threshold. The calculation excludes subcritical crack growth, flaw population statistics, pressurized flat windows, seals, corrosion, fatigue, temperature and pressure cycling. The tool **cannot rate pressure-vessel safety**.

Example default toy parameters:

- Pressure: `29 - 1 = 28 atm`, hence `Δp = 2.8371 MPa`.
- Curved shell `r=0.20 m`, `t=0.010 m`, so `σ=28.371 MPa` under membrane approximation.
- Half crack length `a=0.10 mm` and `Y=1`; `K_I ≈ 0.503 MPa√m`, a ratio ~`0.23` to that one specimen toughness value. **This is not a passing pressure safety test**.
- `κ=0.8 m⁻¹` over `0.5 m` gives passive signal retention ~`67.03%`, which is **not** a measured ALON crack-growth or optical absorption coefficient.

**Actual ALON optical loss would need wavelength, polished finish, thickness and transmission data.** This UI's arbitrary exponential attenuation κ is an unrelated illustrative propagation variable. There is **no claim of inherent self-healing, nuclear fission, Planck membrane, magnetic containment, or gold production**.

## Independent runtime boundary

```text
project root
|
+-- projects/sapphon-li/kelvin.mjs
|      [frozen KELVIN v11.3 / unchanged]
|
+-- projects/xenonite-x0/madre-sapphon/
|      [Aa.Nn.Nn parent + Au79 / unchanged]
|
+-- projects/xenonite-x0/alon-separate/
       index.html               [live track view]
       alon-track.mjs           [separate manual observation engine]
       alon-manifest.json      [machine-readable role/evidence definition]
       README.md               [this document]

       {{ -AaaA....LllL....OooO....NnnN.... }}
          4 motifs, 16 glyphs, 16 delimiter periods

       A   Al atoms
       L   Lattice (non-element)
       O   O atoms
       N   N atoms
```

No child from Madre Sapphon, no new AI agent, no auto-spawn, no rewritten KELVIN state transition or material patent/exclusivity claim.

## Source provenance

- [NASA Glenn, Jonathan A. Salem, _Crack Growth Testing of an Aluminum Oxynitride (AlON) for International Space Station Kick Panes_ (2017)](https://ntrs.nasa.gov/api/citations/20170001289/downloads/20170001289.pdf) — elastic modulus, Poisson ratio, measured K_IC, slow crack growth in tested specimens.
- [Surmet ALON optical ceramics properties](https://cdn.thomasnet.com/ccp/01097403/135889.pdf) — nominal composition and material family.
- [Earlier independent sourced ALON candidate assessment](../MATERIAL-ALON-CANDIDATE.md) — evidence and qualifiers.
- [Original Xenonite-X0 concept](../XENONITE-X0.md) — broader boundary analogy.

**Status notes:** code and web UI are committed and inspectable. Any actual runtime/browser compatibility, mechanical reliability or physical synthesis must be independently assessed; no physical tests, official safety qualification or benchmarks are claimed.
