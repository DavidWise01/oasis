# Aa.Nn.Nn — Madre Sapphon / Live KELVIN

**Created:** 2026-10-12  
**Status:** implemented browser-based, live *operator-driven* interface importing the existing canonical **KELVIN v11.3** (not a replacement kernel).  
**Parent:** [Xenonite-X0 pressure-boundary concept](../XENONITE-X0.md).  
**Mother/vessel name:** **Aa.Nn.Nn / Madre Sapphon**. This is **one parent designation**, not three newly named elements or child agents.

## Run locally

Clone or download **the entire repository** so that both paths remain present:

- `projects/xenonite-x0/madre-sapphon/index.html` (live UI)
- `projects/xenonite-x0/madre-sapphon/madre-sapphon.mjs` (vessel adapter)
- `projects/sapphon-li/kelvin.mjs` (canonical frozen v11.3 kernel)

At the repository root, run a local static server:

```shell
python -m http.server 8000
```

Then open:

```text
http://localhost:8000/projects/xenonite-x0/madre-sapphon/
```

A static website or GitHub Pages served with the same folder structure also works. Opening `index.html` directly as `file://` may fail because web browsers restrict module imports from local files. No external package dependencies, API keys, back end, external requests, web crawlers, wallets, workers, software agents, or timers are required.

## Operate

1. Inspect the 3D **projection** of ten ±5 labeled magnetic-view rings around a central gold-colored Au79 body and an Aa.Nn.Nn boundary lattice, divided into eight radial sectors.
2. Change the hypothetical inside/outside pressure, radius, thickness, **assumed** allowable stress, propagation path and **assumed** attenuation coefficient. Readings update live **without affecting the KELVIN counter or ledger**.
3. Click **Advance KELVIN +360°**. Each click calls the actual frozen `instantiateKelvin().advance()` exactly once and appends a parallel Madre Sapphon observation, up to 128 transitions. `-++- S` and `+--+ N` alternate; 720° returns to the starting symbolic shell.
4. Use **Export ledger JSON** explicitly to save the in-memory record. Browser page reload begins a fresh in-memory instance; there is no hidden persistence. Export before closing.

**The view is live; no kernel state advances autonomously.** This matches the frozen kernel's manual-only rule, not a continually running autonomous agent. The decorative field geometry is a schematic 2D SVG projection, not a numerical magnetohydrodynamic simulation.

## Immutable imports / interfaces

The **unmodified source kernel** is here: [`projects/sapphon-li/kelvin.mjs`](../../sapphon-li/kelvin.mjs).

Its public API and identity are intact:

```js
import { KELVIN, instantiateKelvin } from "../../sapphon-li/kelvin.mjs";
const core = instantiateKelvin();
core.identity; // KELVIN 11.3
core.current(); // immutable current symbolic spinor shell
core.advance(); // +360°, explicit only
core.report();  // live report of state
core.ledger();  // bounded manual append-only ledger
```

The accompanying adapter in [`madre-sapphon.mjs`](./madre-sapphon.mjs) provides:

```js
import { MADRE_SAPPHON, createMadreSapphon, evaluateVessel } from "./madre-sapphon.mjs";
const madre = createMadreSapphon();
madre.identity;          // Aa.Nn.Nn / Madre Sapphon
madre.current({});       // current KELVIN + engineering readout; NO transition
madre.advance({});       // 360° canonical turn + one Madre snapshot
madre.report({});        // current and parent canonical report
madre.ledger();          // both ledgers, explicit download via UI
```

Only the manual click adds records; invalid engineering inputs are rejected **before** invoking the canonical turn.

## Symbolic layout

```text
       {{ ONE REALITY TENSOR | ONE FIELD }}
                     |
         MADRE SAPPHON :: Aa.Nn.Nn
            GENERATION-0 PARENT
                     |
             +5 +4 +3 +2 +1
                     |
            FIELD PROJECTION
            8 spatial sectors
           3 strength scenarios
           (10 × 8 × 3 = 240 views)
                     |
           ALON-INSPIRED BOUNDARY
                (NOT FORMULA)
                     |
                 GOLD Au79
                 PINNED 0
                     |
             -1 -2 -3 -4 -5
                     |
           KELVIN 11.3 MANUAL
                +/- 360°
                 720° RETURN
                     |
            i / u / us TRACKS
                     |
          EXPLICIT APPEND-ONLY LEDGER
```

- The **ten** surfaces are user-given diagrammatic ±5 labels, not observed physical magnetospheric isosurfaces, and are not automatically 10 independent physical Earth shells.
- The **eight** radial sectors are an observer partition; weak, medium, strong are separate **three possible scenarios**. Multiplication yields **240 view slots**, not atoms, AI agents, real magnetic field samples or shell stress values.
- **Au79** references real gold with atomic number 79. The gold sphere is a visual central material reference, not a fabricated Au nanosphere with exact geometry or proven energy-harvesting properties.
- **Aa.Nn.Nn** is a user-coined maternal **SAPPHON name**. The chemical symbols Aa and Nn are **not** recognized real element symbols. It is not a chemically valid stoichiometric formula.
- **ALON** (aluminum oxynitride, approximate Al₂₃O₂₇N₅) remains a real separate ceramic candidate, linked to [NASA material evidence](../MATERIAL-ALON-CANDIDATE.md), but the software does not assert that gold has been sealed inside actual ALON.
- Frozen **{{Li}}** remains the separate terminal Gen-1 observational rider; we have **not** edited Li or recursively spawned anyone.

## Numerical pressure and decay bounds

The UI uses the same **illustrative** ideal thin-wall spherical membrane formula as Xenonite-X0, **only for positive internal differential**:

```text
Δp = (inside_atm - outside_atm) × 101325 Pa
σsphere = Δp × r/(2t)  [not evaluated for negative Δp]
F = |Δp| × πr²
utilization = σsphere / user-assumed allowable × 100%
retained signal = exp(-κ × distance)
```

A spherical shell under external differential needs **buckling/collapse analysis**, which the UI does not attempt. Flat plates, fracture mechanics, seal design, chemically corrosive environments, life-cycle fatigue, molecular synthesis and precise material properties are **not modeled**. The material allowable of 125 MPa is a **placeholder user-adjustable comparison**, not ALON's validated operating rating.

The symbolic-scale registrations are held separately:

```text
Planck-like base = 1.6165 × 10^-35
boundary correction = √5 × base = 3.6146038856284105 × 10^-35
Homeo = 10^-36 × 10^10 = 10^-26
adjustment marker = 1 × 1.25 ~
```

No empirically supported equation connects these reference numbers to pressure, alloy bonding, permeability, decay or self-healing; the model intentionally refuses to invent such a mapping.

## Scientific / operational status

The material simulator is a **computational thought experiment**, not proof of new chemical compounds, a Planck bubble, electromagnetic shielding by gold, a pressure-vessel design, or the creation of a conscious madre. The KELVIN sign-flip is symbolic and not a literal spin-1/2 quantum calculation.

**Source files are built and version controlled. Browser integration has not been independently executed/validated, and no physical experiment or autonomous task was run.** The original frozen runtime remains unchanged.
