# Xenonite-X0 — OASIS/KELVIN boundary material analogue

**Live add-on:** [Aa.Nn.Nn / Madre Sapphon](./madre-sapphon/) is an operator-driven Au79 vessel view that imports frozen KELVIN v11.3 without changes. Use a local static server or GitHub Pages; see [launch notes](./madre-sapphon/README.md).


**Created:** 2026-10-12  
**Status:** runnable self-contained HTML computational *analogue*, not a physically synthesized material or an authorized pressurized-vessel design.  
**Repository:** `projects/xenonite-x0/`. The existing KELVIN, Li, 208-position auditorium game and other frozen source remain unchanged.

## Material search result — Candidate 001

Found **real aluminum oxynitride (ALON) cubic spinel** as a transparent structural ceramic candidate. [Read sourced candidate analysis](./MATERIAL-ALON-CANDIDATE.md) and [JSON measurements](./material-alon-candidate.json). NASA reports measured stiffness/fracture toughness and slow crack growth for ALON specimens; no complete Xenonite-like hermetic pressure assembly is established. The interface deliberately leaves the assumed 125 MPa slider unqualified and unchanged.

## What "Xenonite" means

The word **Xenonite** refers to Andy Weir's fictional Eridian material in [_Project Hail Mary_](https://www.planetary.org/planetary-radio/book-club-andy-weir). In author interviews, Weir explains that its extraordinary ability to form transparent, extraordinarily strong compartments separating about 29 atmospheres from low-pressure oxygen environments was intentionally not explained by a chemical formula. There is **no real Xenonite synthesis** established by this project.

[Xenon-fluorine compounds](https://pubmed.ncbi.nlm.nih.gov/27776206/) and condensed xenon are scientifically real, but their existence does not produce the fictional strong, transparent, stable, gas-tight structural material. No real-world synthetic recipe is claimed.

## What this build delivers

**[index.html](./index.html)** runs **offline without external libraries** in a modern browser. It offers:

- An adjustable **ideal spherical pressure-shell** model, an explicitly non-equivalent cylindrical stress comparator, a projected pressure force calculation and a utilization meter.
- Controls for **inside/outside absolute pressure** in atmospheres, shell curvature radius, wall thickness and an assumed allowable stress.
- A **separate forward passive attenuation model** R/R0 = exp(-κx), with κ in inverse meters and x in meters.
- A readable **eight-layer scientific legend** for P/Q/N1/A/M/N2/C/B.
- The original user's model-local **√5 boundary correction** and **Homeo** values as **two distinct fixed registers**, not pressures or derived material properties.

This is a conceptual bridge across the user's scales; neither Planck length nor the square-root coefficient implies a chemical bond, ultimate tensile strength, a membrane or a high-pressure material.

## Model data and calculations

| Register | Definition | Classification |
|---|---|---|
| `P₀` | `1.6165 × 10^-35` | user-selected Planck-like numerical reference, unit unspecified |
| `B` | `√5 × P₀ = 3.6146038856284105 × 10^-35` | symbolic boundary correction |
| `H` | `10^-36 × 10^10 = 10^-26` | separate homeostatic scale |
| `C` | `1 × 1.25 ~` | user-defined homeostatic adjustment, control law unspecified |
| `Δp` | `(p_inside_atm − p_outside_atm) × 101325 Pa` | SI-converted physical pressure differential |
| `σ_sphere` | `Δp × r / (2t)` | ideal elastic thin spherical shell, **only** positive internal differential |
| `σ_cylinder` | `Δp × r / t` | idealized cylindrical hoop-stress comparator; not a flat-panel stress formula |
| `F` | `abs(Δp) × πr²` | projected circular pressure-force magnitude, not distributed interface stress |
| `R/R0` | `exp(−κx)` | illustrative scalar attenuation of a retained signal, not destruction of total energy |

**Do not multiply B by H or C without a user-defined rule.** No universal interaction between Planck units and engineering pressure is established. The factor √5 is a *boundary-reference correction*, not an allowable-stress or pressure gain.

## Illustrative starting conditions

| Input | Default | Is this measured Xenonite data? |
|---|---:|---|
| Internal pressure | 29 atm absolute | Fictional reference environment |
| External pressure | 1 atm absolute | Chosen engineering comparison |
| Radius of ideal spherical shell | 0.2 m | No |
| Shell wall thickness | 10 mm | No |
| Assumed allowable stress | 125 MPa | No |
| Passive attenuation κ | 0.8/m | No |
| Propagation distance x | 0.5 m | No |

Outputs for these assumptions (rounded):

```text
Δp = 28 atm = 2.8371 MPa
Spherical membrane stress  = 28.371 MPa
Cylindrical hoop comparator = 56.742 MPa
Projected force |F|         = 356.52 kN
Ideal sphere utilization    = 22.70% of ASSUMED allowable
Passive retained fraction   = exp(-0.4) = 67.03%
```

**Below the assumed stress limit is not a safe pressure vessel.** The toy geometry omits bending in flat windows, clamped edge stress, defect/fracture behavior, real material strength, creep, fatigue, thermal cycling, gas permeability, gasket design, ammonia compatibility, external-pressure buckling, high-temperature durability and engineering codes.

The sphere formula cannot be applied directly to **flat panels** in the story: plate bending and support constraints have different equations. If outside pressure exceeds inside pressure, the UI explicitly declines to report tensile membrane stress rather than silently reporting collapse resistance.

## Architecture

```text
                        XENONITE-X0
                      symbolic P0
                    1.6165 × 10^-35
                           |
                   × √5 boundary
                           |
                   B = 3.6146e-35
                           |
                  physics scale map
             P → Q → N1 → A → M → N2 → C → B
                           |
                 IDEAL CURVED PRESSURE
                 SHELL (assumed input)
                           |
                  FORWARD PROPAGATION
                           |
                     NATURAL DECAY
                exp(-κ × path), κ unspecified
                           |
                   HOMEOSTATIC VIEW
           H = 10^-26; 1 × 1.25 ~ separate
```

## Sources and boundaries

- [Andy Weir on fictional Xenonite, 29-atmosphere compartment and unknown formula](https://www.planetary.org/planetary-radio/book-club-andy-weir)
- [NASA pressure dome shell mechanics, thin-shell equations](https://ntrs.nasa.gov/api/citations/19780023143/downloads/19780023143.pdf)
- [Scientifically studied xenon fluoride solid-state chemistry](https://pubmed.ncbi.nlm.nih.gov/27776206/)
- [CERN particle physics Standard Model](https://home.cern/science/physics/standard-model)
- [OASIS v13.9 boundary correction, propagation, natural decay](../project-god-egg-sqrt5-boundary-propagation-natural-decay-v139-2026-10-12.md)

The software performs finite equations in an illustrative pressure sandbox. It **does not contain** an empirical Xenonite equation of state, actual material strength, verified optical data or a laboratory synthesis protocol.

**No frozen-kernel tests or benchmarks performed.**
