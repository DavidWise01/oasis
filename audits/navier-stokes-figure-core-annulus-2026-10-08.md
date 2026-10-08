# Visual and physical-boundary audit — OpenAI Navier–Stokes proof
Date: 2026-10-08
Sources:
- https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf
- https://arxiv.org/pdf/2610.08144

## Figure inspection
Figure 1 on printed page 4 (PDF page index 3) depicts a shrinking swirling inner core with an axial jet in opposing +/-z directions. Original paper section 2 specifies inward spiraling at the core, upward/downward movement across z=0, and further radial outflow higher/lower away from the central region. Figure 1 is expressly a schematic of the *central part*, not the entire field.
Figure 2 on printed page 5 (PDF index 4) represents complete concentric pulse envelopes in the annulus and radial–axial patches with perturbation velocity arrows.

## What the authors claim
Original Theorem 1.1 states a smooth compactly supported force f, velocity u and pressure p on R^3 x [0,1), divergence-free u, zero initial velocity, bounded kinetic energy and unbounded velocity at t -> 1. The authors explain that the leading vortex and exterior have a momentum residual in the annulus; oscillatory pulses plus corrections are designed to cancel its singular portion, leaving smooth forcing. A toroidal *closed streamline* is not stated as a requirement.

## Audit interpretation
- VERIFIED: inward spiral / axial outflow in core schematic; annular residual is acknowledged; corrections are proposed.
- NOT ESTABLISHED: missing gravitational closure. In incompressible PDE a spatially uniform conservative body force can be included in the pressure gradient. A toroidal domain is not the same as a closed vortex streamline.
- OPEN: verify complete matching across inner core -> annulus -> exterior, smoothness of forcing at t=1, divergence-free condition and exact final theorem against Lean version and NL assumptions.
- Existing arXiv 2610.08144 concerns NL-to-Lean correspondence, not a confirmed physical fluidic-toroid geometry counterexample.
- The earlier zero Fourier mode is a spatial average, not a geometric center coordinate.

Verdict: AXIAL OUTFLOW CONFIRMED / GEOMETRIC-FAILURE CLAIM UNPROVEN.
