# ROOT0 — P2.0 First dimensionful physical prediction and first failed lattice mapping

**Status:** 2026-10-08; numerical/model derivations PASS, straightforward Planck-length cubic mapping FAIL, proposed alternative only CONDITIONAL. The actual-world simulation hypothesis remains UNPROVEN.

## Exact proof target

The preceding P1.1–P1.8 work proves and exhaustively tests formal properties of finite symbolic toroidal states and append-only witness histories. It does **not** supply any independently grounded map from the 5-node toroid / 55,296-state witness schema to electromagnetism, the 3+1-dimensional spacetime metric, or laboratory seconds and meters.

Therefore this P2.0 test introduces an **additional and explicitly labeled physical candidate**, chosen to generate a falsifiable prediction. It is **not** a deduced consequence of the original frozen I13 or AE-v92 kernel. The point is to challenge a physically meaningful bridge rather than treat resemblance or historical permutation as proof.

## Hypotheses

- **H0 (ordinary vacuum propagation):** in local inertial spacetime, massless electromagnetic waves have group speed `c` independent of energy and direction. The propagation contribution to an energy-dependent vacuum delay is zero. Emission and medium effects are separate nuisance terms.
- **H1 (added cubic-lattice scalar wave, not Maxwell theory):** a real scalar field `u^n_(i,j,k)` obeys the 3D second-order centered-difference wave rule

  `u^(n+1)_j - 2 u^n_j + u^(n-1)_j = r^2 Σ_(α=x,y,z) (u^n_(j+eα) - 2u^n_j + u^n_(j-eα))`,

  where `r = c τ / a`, `a` is cubic spatial pitch [m], `τ` is a tick [s], `c` is m/s. This *scalar* discretization intentionally ignores gauge constraints, Maxwell polarization, dynamical gravity, curvature, quantum measurement and the original kernel's `in/out` semantics.

Fourier modes obey

`sin²(ω τ / 2) = r² [sin²(kx a/2) + sin²(ky a/2) + sin²(kz a/2)]`.

Because the right-hand side reaches `3 r²`, a real propagation frequency for every spatial Fourier mode requires `3 r² ≤ 1`. At equality the highest-frequency corner mode is **marginal**, so robust stability prefers strict inequality.

## P2.0-A: Test the natural unmodified Planck mapping — FAIL

Use the user's 1 Planck-time-per-tick (`τ=t_P = l_P / c`) and make each cubic edge one Planck length (`a=l_P`). Then `r=1`, so at a 3D Brillouin-zone corner with `kx a=ky a=kz a=π`, RHS=`3 > 1`: there is **no real ω** satisfying the dispersion relation. Equivalently the recurrence for that spatial mode has `λ²+10λ+1=0`, with growing root magnitude `5+sqrt(24) = 9.898979...` per tick. This invalidates this particular 3D scalar-wave discretization with those spacetime assignments; it does NOT invalidate other automata, quantum walks, spacetime discretizations, or simulation theory.

## P2.0-B: Stable/borderline added mapping and dimensional prediction

Keep `τ=t_P`, choose `a=√3 l_P`, so `r²=1/3`, the marginal CFL boundary. Under this extra hypothesis, a wave with magnitude `k` traveling along a cubic axis has

`ω(k) = (2/τ) arcsin[(1/√3) sin(ka/2)]`,

and radial group velocity

`v_axis / c = cos(ka/2) / sqrt[1 - sin²(ka/2)/3] = 1 - (ka)²/12 + O((ka)^4)`.

For the body diagonal `n=(1,1,1)/√3`, the dispersion simplifies exactly in the first Brillouin zone to `ω=ck`, `v_diag=c`, with zero model vacuum delay at leading and indeed every order in that special direction.

For arbitrary unit direction `n=(nx,ny,nz)` and small `ka`, leading order is

`v_group,radial/c = 1 - (ka)² (nx⁴+ny⁴+nz⁴ - r²)/8 + O((ka)^4)`.

This predicts an energy-quadratic correction and a specific **cubic (fourth-order angular)** anisotropy, unlike isotropic special-relativistic propagation. The axes would need an independently constrained orientation to preregister an empirical test.

Using `E≈ℏ c k`, for high and low photon energies and flat-space propagation baseline length `D`, the axis-mode delay is

`Δt_axis ≈ (D/c) * [a²/(12(ℏ c)²)] * (E_hi² - E_lo²)`.

Constants from NIST CODATA 2022:
`c=299792458 m/s` exact, `ℏc≈0.1973269804 GeV fm`, `l_P=1.616255e-35 m`, `t_P≈5.391247e-44 s`.
For **D=1 gigaparsec** and 30 GeV versus 1 GeV photons, a=`√3 l_P` yields **Δt_axis ≈ 1.55194514e-19 seconds**, body diagonal zero. The required hypothetical **1 ms sensitivity** would correspond to `a≈2.24715e-27 m` for the same energies and distance, about **80 million** times the proposed `√3 l_P` pitch; *1 ms is only a benchmark sensitivity, not a reported instrument measurement*. To reach a 1 ms delay at the assumed Planck pitch would require a photon energy roughly 2.41e9 GeV in this flat-space toy, completely outside the demonstrated source assumptions.

## P2.0-C: Interior stable alternative exposes parameter underdetermination

Keep τ=t_P but choose `a=2 l_P`, yielding `r=1/2`, `3r²=3/4<1`, strictly within the CFL requirement. Then the same D/E benchmarks give **Δt_axis≈2.327918e-19 s** and **Δt_diag≈2.586575e-20 s**, showing that the original kernel's clock constraint does **not** uniquely fix physical dispersion when the spatial geometry is unspecified. It is illegitimate to pick spacing after inspecting any experimental data and declare a successful prediction.

## Empirical baseline and existing measurement

In 2009 the Fermi collaboration observed a ~31 GeV photon from GRB 090510. *Nature* (doi:10.1038/nature08574) found no evidence of a **linear** Lorentz-violating energy-dependent light speed. A 2013 Fermi analysis in *Physical Review D* (doi:10.1103/PhysRevD.87.122001) reported bounds on **quadratic** LIV in a given isotropic parameterization (E_QG,2 > 1.3e11 GeV, 95% CL, subject to source assumptions). The particular Planck-pitch toy predicts extremely small **quadratic and anisotropic** dispersion, far too tiny to infer from these observations without the proper redshift integral, source-emission model, directional axis and sensitivity analysis. **The published Fermi bounds do not prove H1 or simulation theory.** No existing dataset has been reanalyzed here; the 1 Gpc flight is an illustrative static-metric scenario, not a reconstructed GRB 090510 light path.

## Falsifiability and preregistration

A defensible physical test must predeclare `(a,τ)`, gauge dynamics, a single preferred-frame axis orientation or its independently constrained prior, the source-emission time model, cosmological redshift integral, instrument resolution, directional cubic harmonic, uncertainty handling, analysis code, and a rejection threshold. Test many independent photon source events across the sky against H0, not one cherry-picked time coincidence. A non-detection becomes discriminatory only after measurement sensitivity reaches the parameter-free H1 prediction. A detection at some fitted spacing is NOT unique evidence for simulation because other Lorentz-violating EFTs, dispersive media and source astrophysics can resemble it.

## Test results and formal status

- Node 22 numerical assertions PASS, model dispersion and analytic expansion match down to dimensionless ka=1e-4 within floating-point accuracy.
- Planck cubic map a=l_P, τ=t_P: analytic high-frequency instability counterexample PASS.
- Added marginal a=√3 l_P: conditional analytic dispersion and numerical time-of-flight prediction PASS.
- Added interior a=2 l_P: strictly-stable CFL inequality and different predicted delays PASS.
- Lean source is a proof **DRAFT**, not compiled in this session.
- No Maxwell-field equivalence, physical coupling to the frozen ROOT0 toroid, pre-registered observation, or proof of external simulation.

**Next gate P2.1:** Try to derive the wave dynamics and calibrated axes from the frozen ROOT0 rules, *without adding unconstrained parameters*. If impossible, record non-identifiability and design a genuinely discriminating preregistered experiment instead of claiming a physics victory.

## Reproduction

`node p20_dispersion_test.mjs` regenerates `p20-results.json` and prints the calibration/stability status. `P20ConditionalLattice.lean` records rational-CFL lemmas but requires an independent Lean 4 compiler run.

Sources: NIST 2022 CODATA https://physics.nist.gov/cuu/pdf/all.pdf ; Fermi 2009 https://www.nature.com/articles/nature08574 ; Fermi 2013 https://doi.org/10.1103/PhysRevD.87.122001 .