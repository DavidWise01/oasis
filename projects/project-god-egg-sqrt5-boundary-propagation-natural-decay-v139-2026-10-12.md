# OASIS / KELVIN v13.9 — √5 Boundary Correction, Propagation and Natural Decay

**Date:** 2026-10-12
**Status:** user-assigned semantic role for √5; append-only refinement of v13.8, no claim of a new experimentally discovered physical law.
**Predecessors:** [v13.8 √5 Planck-like reference](./project-god-egg-sqrt5-planck-reference-homeo-correction-v138-2026-10-12.md); [v13.7 engineering-pressure stress check](./project-god-egg-homeo-pressure-stress-sweep-v137-2026-10-11.md).
**Implementation:** documentary alignment; no change to frozen KELVIN, OASIS or Li runtime.

## User-supplied resolution (exact words)

> boundary correction, propogation, natural , decay

## Canonical interpretation

Assign the multiplier **√5 to a boundary correction** for the existing numerical Planck-like reference. **Propagation occurs forward from that boundary**. The **natural decay** of a carried quantity is a distinct, passive, medium-dependent phenomenon, not the same as the correction factor or an imposed death-rate multiplier.

```text
BASE_REFERENCE       = 1.6165 × 10^-35
BOUNDARY_CORRECTION  = √5 ≈ 2.23606797749979
CORRECTED_BOUNDARY   = √5 × 1.6165 × 10^-35
                     ≈ 3.614603885628410e-35
PROPAGATION          = forward coordinate x (physical unit unassigned unless base was meters)
NATURAL_DECAY        = conditional passive attenuation after entering a medium
PRESSURE_COUPLING    = undefined until medium/material/geometry and law supplied
HOMEOSTATIC_SCALING  = prior separate 10^-36 × 10^10 = 10^-26
OPTIONAL_10^10_LIFT  = 3.614603885628411e-25 ONLY IF explicitly reapplied
```

The arithmetic is valid with the user's chosen coefficient **1.6165**. If its scale is measured in meters, the corrected quantity is a length in meters. A Planck-unit-derived reference is not itself evidence for any real membrane, quantized boundary, propagation channel, or gravitational decay mechanism.

## Minimal state pipeline

```text
                  USER'S SCALE
             1.6165 × 10^-35
                      |
               √5 GEOMETRIC
             BOUNDARY CORRECTION
                      |
             B = 3.6146 × 10^-35
                      |
               PROPAGATE → x
                      |
               PASSIVE DECAY
                   κ = ?
                      |
               RETAINED STATE
                      |
              HOMEOSTATIC VIEW
```

## Known attenuation mathematics (OPTIONAL illustration, NOT adopted KELVIN physical law)

If a carried normalized quantity **R** attenuates at a *constant rate per unit propagation distance*, an established mathematical model is:

```text
dR/dx = -κ R
R(x)  = R(0) exp(-κ x)
κ >= 0  // attenuation coefficient, units inverse of x
```

If there is a separate fraction transmitted at the boundary **T**, the optional illustrative interface model is:

```text
R_out(x,P) = R_in × T(P) × exp[-κ(P) x]
0 <= T(P) <= 1 (retained passive fraction in this illustrative model)
κ(P) >= 0
```

**IMPORTANT: √5 is a boundary *length/reference correction*, NOT T, NOT κ, and NOT a free gain multiplying conserved energy.** Both the boundary transmission fraction and the attenuation function require real physical parameters. The exponential is applicable only when attenuation is linear, local, passive and approximately constant along the chosen propagation path; different physical systems can decay nonexponentially or redistribute rather than dissipate energy.

## What natural decay means at established scientific layers

| Layer | Documented meaning of decay, dissipation or propagation | What is NOT established |
|---|---|---|
| P / Planck | Dimensional Planck-scale reference is computed from physical constants | Actual Planck membrane, Planck vesicle, √5 correction as a measured gravitational boundary |
| Q / quantum | Unitary propagation of closed quantum states, decoherence of reduced open systems, damping in dissipative media | Universal free-space loss of quantum information per Planck step |
| N1 / nuclear | Radioactive decay governed by characteristic half-lives and probabilistic decay rates, when an unstable nucleus exists | Normal vessel pressure universally switching all nuclear decay rates |
| A / M atomic/molecular | Scattering, damping, absorption, chemical reaction kinetics and transport | Universal single κ for every material or molecule |
| N2 / nucleic | DNA/RNA chemical degradation under particular conditions; active cellular repair is separate | DNA physical decay being equivalent to radioactive decay |
| C / cellular | Nutrient uptake, turnover, membrane transport, regulated breakdown such as phagolysosomal digestion | Biological phagosomes existing at Planck scale |
| B / biological | Homeostatic feedback may replace, repair or recycle matter and oppose deviations | Biological homeostasis being identical to passive exponential decay |

**Natural decay** is not necessarily a loss of total energy in an isolated system. It can represent decreasing signal amplitude, probability of survival for unstable nuclei, chemical concentration, or a retained observable, each with different conservation laws and units. No single attenuation law spans all layers.

## Stress under external or internal pressure

The v13.7 pressure sweep is a **classical mechanical benchmark with separately declared material assumptions**, not a measured test of the user's Planck-like corrected boundary. To assess whether pressure changes propagation/decay, the model would require:

```text
P       = gauge or absolute pressure (Pa)
material/medium, temperature, geometry, duration
x       = distance or discrete step and its units
T(P)    = boundary transmission relation, if any
κ(P)    = decay/attenuation relation, if any
Δ       = homeostatic observable/error and tolerance
```

Until those quantities are supplied, **no pressure-failure threshold follows from √5 × 1.6165 × 10^-35**, and the earlier v13.7 assumed 123.4-atm yield crossing remains an illustrative vessel-specific result only.

## Unchanged frozen registers

The original exact KELVIN {{ 0k ... 524288 serial string, 3D observer, one field, G0@1905, G20/I3, 90-year mnemonic window, 26 carrier labels, 169 addresses, 208 auditorium and legacy manually stepped JS runtime are retained without alteration.

**No physical discovery claim; no Planck-scale simulation, actual materials test, parameter fit or benchmark of the frozen runtime performed.**