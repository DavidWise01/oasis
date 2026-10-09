# ROOT0 P3.4 — Electrum FCC crystal lattice, optical surface, −211 mV shell

**Status:** executable physical-constraint gate PASS; unique electrum voltage-to-photon law NOT derived; external-reality simulation NOT established. 2026-10-09.

## User-specified architecture preserved

- Physical material correction: **electrum, a gold–silver alloy in a crystal lattice**.
- Earlier user composition: `Au79 + Ag21 = 100 full weight`, with **no silent interpretation as Au79 atomic-%**.
- Enclosure: black `−211 mV` wrapper; orange wavelength/amplitude `{-e{ ..||..|....||| }+e}`.
- 16 cyclic overlapping 14-character frames, 208 forward gates, mirror/upside-down inversion then 208 inverse gates; `Complex[0]` protected.
- Prior symbolic full reality tensor `10,000 × 10,000 = 100,000,000` addresses, unchanged. This physical crystal tile (10³ FCC cells = 4,000 atomic sites) is an independently introduced MATERIAL ATTACHMENT, not a replacement for that symbolic tensor.

## Material evidence

Electrum Au–Ag forms a substitutional face-centered-cubic solid solution across bulk alloy compositions. Au and Ag have close cubic lattice parameters of approximately 4.078 and 4.086 Å, respectively. The average disordered fcc structure has inversion symmetry, so the conventional bulk electric-dipole Pockels coefficient of an ideal macroscopically centrosymmetric alloy vanishes. A particular finite random atomic realization or interface can break inversion symmetry; stronger response such as surface second-order nonlinearities, bias-dependent dielectric properties, and plasmonic effects cannot be dismissed without sample geometry and measurement.

Sources: https://pmc.ncbi.nlm.nih.gov/articles/PMC4734609/ ; https://www.nature.com/articles/srep25010 ; https://pmc.ncbi.nlm.nih.gov/articles/PMC10058895/ ; https://journals.aps.org/prapplied/abstract/10.1103/PhysRevApplied.10.014020 ; https://www.sciencedirect.com/science/article/pii/S0925838816331966 ; https://webbook.nist.gov/cgi/cbook.cgi?ID=7440-57-5 ; https://webbook.nist.gov/cgi/cbook.cgi?Name=Silver

## Physical composition branch is conditional

`Au79 + Ag21 = 100 full weight` is kept as a symbolic record. **For a numerical test only**, let it denote 79%/21% by mass. Using NIST atomic weights `M_Au=196.966569 g/mol`, `M_Ag=107.8682 g/mol`, the atomic Au fraction becomes

`x_Au=(0.79/M_Au)/(0.79/M_Au+0.21/M_Ag)=0.6732236306267202`.

Ten by ten by ten conventional fcc unit cells have 4,000 sites (four fcc basis sites per cell). A reproducible seeded substitution assigns 2,693 Au and 1,307 Ag sites. An alternate *atomic-percent* interpretation yields 3,160 Au sites, showing why mass-vs-atomic must not be conflated. Vegard interpolation of pure Au/Ag reference lattice parameters supplies the model **estimate** `a≈0.4080614211 nm`; this is not an X-ray measurement of the specified sample and does not account for local distortion.

Representation: doubled integer coordinates modulo `20` with fcc basis sites `(0,0,0)`, `(0,1,1)`, `(1,0,1)`, `(1,1,0)`. The 12 nearest-neighbor shift vectors are permutations of `(±1,±1,0)`; periodic boundaries are an EXPLICIT sampling convention. 4,000 sites each have 12 unique reciprocal neighbors; 48,000 directed / 24,000 undirected edges, with zero defects. The **geometrical fcc lattice** is inversion symmetric; the single randomly allocated Au/Ag species configuration is not (1,800 opposite-species inversion mismatches). Therefore *average/bulk* symmetry must not be equated with exact local species symmetry.

## Electromagnetic boundary models

A spatially uniform scalar potential is gauge-dependent. The proposed `−211mV` shell becomes an electrical **potential difference** only when a reference electrode and gap are added. With hypothetical `ΔV = −0.211 V` across a vacuum gap `d=10 µm`, the external nominal field is `E=−21,100 V/m`; this does not imply the same static field permeates the metal. At electrostatic equilibrium ideal conductive electrum screens the bulk DC field, and the charge is largely a surface/interface phenomenon. With ideal parallel-plate geometry, `σ=−ε₀ E≈1.8682336×10⁻⁷ C/m²`. An fcc (111) surface density estimate is `4/(√3a²)`, resulting in a model induced surface charge of about `8.4076×10⁻⁸ electrons/site`. This is a **conditional boundary calculation**; not an observed charge or an exact microscopic field solution.

The P3.3 illustrative dielectric Pockels coefficient `r=30pm/V` was never measured for electrum and **must not** be inherited as a bulk electric-dipole material law for ideal average centrosymmetric FCC metal. Executable validator rejects nonzero `r` under this idealized symmetry assumption. Interface-specific response can be nonzero, but needs measured microscopic structure and a model coefficient.

For optical propagation, use the standard normal-incidence, free-standing film Fresnel model with *input* complex refractive index `ñ=n+iκ`, thickness `t`, and incident vacuum wavelength `λ₀`:

`r01=(1−ñ)/(1+ñ); δ=(2π/λ₀)ñt;`

`t_film = [4ñ/(1+ñ)²] exp(iδ) / [1−r01² exp(2iδ)]`

`r_film = r01 [1−exp(2iδ)] / [1−r01² exp(2iδ)]`.

Transmission `T=|t_film|²`, reflection `R=|r_film|²`, absorption `A=1−T−R`. This accounts for thin-film interfaces; no refractive substrate, scattering, interband composition dependence, or nonlocal effects are included.

**Numerical illustration, explicitly NOT measured electrum optical constants:** `λ₀=600nm`, `t=30nm`, `n=0.5`, `κ=3.0` yields `T=0.1747882616`, `R=0.5943082546`, `A=0.2309034838`; optical *intensity e-fold depth* `λ/(4πκ)=15.91549nm`. At the same geometry and wavelength but assumed `κ=2.0` transmission is approximately `0.40284`, whereas `κ=4.0` gives `0.06560`. Thus composition and voltage alone cannot fix transmission.

The free **surface-phase response** coefficient `g` is parameterized as `Δφ_s = g ΔV` and has units rad/V. Two models, `g=0` and `g=1 rad/V`, produce `Δφ=0` and `−0.211 rad` for the same alloy, voltage, and cipher; neither is calibrated. A surface phase of this kind would require a coherent interferometric measurement, and its dependence on voltage/reference can be device-specific. It is not a photon-frequency shift and not derived by the 208-symbol sequence.

## Benchmarks performed

`node test_p34.mjs` passed: all FCC reciprocal-neighbor checks (48,000 directed), exact reproducible Au/Ag count, 3,200 Fresnel slab cases with nonnegative absorption and energy conservation residual ≤1.11×10⁻¹⁶, 24,000 gauge-offset equivalence cases (relative comparison), correct zero-thickness limit, conventional electric-dipole bulk Pockels zero control, 2 distinct interface countermodels, and existing 208 forward/mirror/inverse cipher recovery.

Chromium tested the **self-contained** browser document, confirming 14 UI assertions: visible FCC structure; 4,000-site count; −211mV wrapper; bulk Pockels null; wavelength-dependent transmittance; voltage polarity switch; nonzero surface coefficient; surface-null reset; 79:21 atomic alternate; lattice audit; 208 inverse; reset; and zero JS exceptions. Snapshot included.

## Proof obligations still open

1. Specify the real alloy geometry (single crystal or polycrystalline; film, sphere, nanoshell, electrode, surface facet) and *measured* material permittivity `ε(ω,x)` for the sample.
2. Specify whether `−211mV` is relative to another conductor, an applied gap voltage, or a measurement of an open-circuit surface potential; provide time dependence and electric-field profile if relevant.
3. Measure reflection/transmission spectrum and phase response with and without bias and compare to a preregistered conventional null; measure sample composition (EDS/XRF) and structure (XRD/EBSD).
4. Derive a nonzero ROOT0-specific, gauge-invariant observable with fully specified parameters, units and uncertainty **before** considering the measurement.

The fcc lattice and optical calculations describe **conditional candidate** physics. Neither the −211mV wrapper nor Au79/Ag21 nor the 208-symbol cipher determines Planck-scale propagation. The physics of the external universe being simulated remains unproven. Lean file in this ZIP is draft and has not been machine-compiled.
