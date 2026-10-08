# Zero-mode versus fluidic toroid: geometry audit note (2026-10-08)

Source pinned at openai/NavierStokesAndEuler@f9e8bc5.

The user proposes a center-0 three-branch construction with an upward offshoot, contrasting this with a closed fluid-circulation toroid. We preserve it as a TEST HYPOTHESIS, not as a verified topology failure.

## Verified upstream definitions
File NavierStokes/ParametricTorusInverse.lean:
- Point := ℝ × Plane and Source := Point → ℂ.
- mean f p := coefficient f p 0.
- ZeroMean f := ∀ p, mean f p = 0.
- mean_eq_integral identifies mean with integral over 0..1 × 0..1.
- Periodic f requires unit periodicity for each slice.
These definitions show zero is a *Fourier zero mode/spatial mean*, not a physical origin or zero at the center of a fluidic vortex.

File NavierStokes/TorusCoverLattice.lean:
- indexMap in relevant proofs maps (x,y) to (3x+y,x+5y).
- integer matrix determinant = 14 and coverRange_index d = 14^d.
- This is a lattice cover, not three 1/3 physical radial branches.

## Important distinctions
A periodic torus domain does not mean all streamlines form closed circles, nor does it imply a fluidic toroidal vortex. Conversely lack of a prescribed vortex streamline is not a defect in a theorem whose object is periodic Navier–Stokes PDE data. No verified branch-offshoot defect has been located.

## Candidate falsification checks
1. Identify exact physical/toroidal-flow claim in the article being audited.
2. Check if it asserts closed trajectories, zero normal flux, divergence-free velocity, pressure recovery, or periodic boundary identification.
3. Follow theorem names to assumptions and final results; do not substitute pictorial notions of zero for Fourier mean zero.
4. If a specific closure statement is missing from a claimed conclusion, record precise statement and countermodel.
5. Compile original Lean before declaring theorem failure.

## Status
ZERO-MODE SEMANTICS VERIFIED / THREE-BRANCH CLAIM UNTESTED / NO PHYSICAL TOROID CLAIM ESTABLISHED.
