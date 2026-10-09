# ROOT0 P3.5 — Electrum spectrum and cipher identifiability audit

**2026-10-09 · P3.5 numerical test PASS; a unique new ROOT0 optical prediction is NOT derived.**

## Measurement provenance and distinction

Johnson and Christy (1972) measured pure gold and silver complex optical refractive indices over a broad range (DOI: 10.1103/PhysRevB.6.4370). This gate reproduces **44 paired wavelength points**, using the CC0 refractiveindex.info data files, Git blobs **cf2f1b2c490d60bea818096920e323da94bbb540** and **fcace717cd05616f344cf732784253260d5c3769** for Au and Ag. These are **not measured electrum alloy values**. Independent measurements of alloy dielectric functions show pure-metal mixing rules can fail; see *Noble Metal Alloys for Plasmonics*, ACS Photonics (2016), DOI:10.1021/acsphotonics.5b00586 and Peña-Rodríguez related modeling, DOI:10.1016/j.jallcom.2016.10.086.

The user notation `Au79+Ag21=100 full weight` is preserved; the demonstration assumes **79:21 by mass**, implying a gold *atomic fraction* **0.6732236306** using Au mass 196.966569 and Ag mass 107.8682. An atomic-percent switch is separately supported. These are explicit test assumptions.

## Two competing metal optics predictions

1. **Permittivity mixing:** `epsilon_mix=x*epsilon_Au+(1-x)*epsilon_Ag`, `N_mix=sqrt(epsilon_mix)` passive square-root branch.
2. **Index mixing:** `N_mix=x*N_Au+(1-x)*N_Ag`.

Both use measured Au/Ag inputs but are *modeled alloys*, not true measured AuAg response. At a free-standing vacuum/30nm-film/vacuum geometry and λ=600nm:

- Dielectric mixing: **T = 0.1380535843; R = 0.7842103809; A = 0.0777360348**.
- Index mixing: **T = 0.1410398388**, distinct by 0.298625 percentage points.
- At 450 nm the two T estimates are about 20.592% and 18.151%; at 800 nm about 5.554% and 5.593%.

Calculations use exact normal-incidence slab Fresnel multiple reflections with the usual `R=|r|²`, `T=|t|²`, `A=1-T-R`. Both mixings reproduce pure elemental endpoints. Material-specific disorder, temperature, grain size, measured dielectric susceptibility and a substrate are *not* supplied. Neither mixing rule is presumed Kramers-Kronig exact.

## Actual cipher-derived mathematical result, versus added physics

P3.1 declared a 16-window one-symbol-overlap and polarity-alternation convention to create 208 dot/bar positions from the original 14-symbol `..||..|....|||`. Encode dot=+1, bar=−1 and compute normalized DFT `S_m=(1/208)Σ_j s_j exp(-2πijm/208)`. There are 104 of each symbol, zero DC, total Fourier power ~1 and dominant mode **m=24**, magnitude **0.3830068447**. That discrete spectrum is a valid *model-local computation*, not an optical frequency. No measured lattice length or physical dielectric coupling between those indices and photons is specified.

Two different electromagnetic attachments honor identical 208-state evolution and same shell `-211mV`:
- Null attachment: `gamma=0`: no additional phase.
- Conditional attachment: `gamma=2 rad/V`, free pitch `p=500nm`: `delta phi=gamma (V-V_ref) |S_24| cos(2π*24*p/lambda)`; at 600nm gives **−0.1616288885rad**.

The conditional phase acts only on a coherent optical phase (unitary modulus one), so both produce **exactly the same T/R/A**. An additionally hypothesized interferometer with visibility 0.85 and reference phase π/2 distinguishes them, illustrating *nonidentifiability*, not a verified novel signal. The coefficient gamma and pitch p are not derived from ROOT0. Uniform potential offsets leave the potential difference and conditional phase invariant; a constant absolute potential cannot independently cause a measurable optical effect.

## Test ledger

- 44 paired pure-metal table rows checked and no out-of-range extrapolation.
- 5,000 sampled films under both alloy rules; max power-identity residual **1.11e−16**; all passive in tested range, method spread up to **0.0424178** absolute T.
- 24,000 common-mode voltage/gauge offsets preserve observable phases and contrasts, residual zero.
- DFT mode 24, zero DC and Parseval ~1.
- 120 complete 208-forward/mirror/208-inverse recovery passes.
- Self-contained Chromium explorer passed wavelength, alloy mixing, zero voltage, hypothetical coupling and reset tests, with zero JavaScript errors.
- Frozen v92 CANON SHA256 **8f2be8951098c7e1764c3c0f5bba982fb3fd8c71f094924b79d0172a313a7bf8**. No modification to frozen v92.

**Conclusion:** no uniquely derived electromagnetic, Planck-scale, photon, or real-universe simulation effect. Pure Au/Ag measured reference data are not measured electrum alloy dielectric data. Lean draft is not machine compiled.

**Next gate P3.6:** use genuinely measured *Au79/Ag21 alloy* spectroscopic ellipsometry of specified fraction, film and boundary; preregister the specific gauge-invariant 208-to-optical coupling (including its physical pitch and parameter value) and a held-out interferometric voltage sweep. A fitted or after-the-fact coefficient is not a prior prediction.
