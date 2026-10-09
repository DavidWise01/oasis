# ROOT0 P3.2 — −211 mV black wrapper around orange amplitude

**Status: conditional model and browser PASS; no measured Planck-scale descent.**
Date: 2026-10-09. Frozen AE-v92, P2.9 tensor and P3.1 cipher kept unchanged.

## Corrected input

The black enclosure is an **electrical potential of −211 millivolts**, not just a color. Its orange interior holds wavelength and complex amplitude. Retain `{-e{ ..||..|....||| }+e}`, 16 interlocking 14-symbol frames, 208 forward operators, 208 mirror-conjugated inverse operators, a pinned `Complex[0]`, and a 10,000 × 10,000 symbolic tensor.

## Explicit voltage dynamics — additional assumption, not derived physics

For formal port charges `q−=−e`, `q+=+e`, voltage `V=−0.211 V` gives opposite potential energies `E−=+0.211 eV`, `E+=−0.211 eV`. Define
`D=diag(exp(−i E− Δt/ℏ),exp(−i E+ Δt/ℏ))`, `ℏ=6.582119569×10⁻¹⁶ eV·s`.
At illustrative `Δt=10⁻¹⁵ s`, the phase magnitudes are `0.32056543152718286 rad`. For original cipher gate `U_t`, forward operator `F_t=D U_t` is unitary. If `M` swaps ±e ports and mirrors/reflects the tensor address, the correct return is `M F_t† M⁻¹ = (M U_t† M⁻¹) D`. In the mirrored frame, the same D is applied before the P3.1 inverse-mirrored gate; omitting it fails adversarial recovery.

**A scalar potential is gauge-dependent.** A constant potential does not by itself prove a measurable photon interaction. A charged-port phase difference would require a separately justified coherent gauge-invariant reference/interference arrangement and applicable boundary conditions.

## Planck levels / independent logarithmic zoom

For comparison only, `0.211 eV` converted to a *single-photon equivalent* gives `λref=(hc)/(0.211 eV)=5.876028361763045 μm`. Define a user-interface log coordinate `ℓ(d)=λref(ℓP/λref)^d` for `0≤d≤1`, `ℓP=1.616255×10⁻³⁵m`. It spans `29.560574001916343` decimal orders; at 100%, the display is marked ℓP. This coordinate does **not** change actual wave energy or claim -211mV transmits physical matter/photons down to ℓP. An independent dynamical calibration is required.

## Executed tests

Local Node v22: 1,200 complete 416-gate wrapped forward/inverse cycles, i.e. 499,200 wave gate applications, **all passed**. Max recovered-component error `3.707397181818817e−14`; max amplitude-norm drift `8.493206138382448e−14`. Negative controls (voltage omitted during inverse, invalid depth and timestep, pinned-zero disruption) passed. Local Chromium via HTML set_content: 208-step forward, mirror/flip, 208-step backward, slider endpoint ℓP, automated 416-gate cycle, 12-case browser regression, all PASS without JS errors. Direct local URL navigation is restricted in this environment, so full standalone HTML is also supplied in ZIP.

The tested P3.2 source modules have byte-matching Git blobs in `docs/reality-tensor/voltage211/`. Downloadable ZIP contains standalone HTML, modular source, screenshot, tests, Lean draft, SHA-256 manifest and the complete report.

## Limits and next proof

Orange field and −211mV shell are an executable *conditional symbolic model*, not a validated physical confinement boundary. A voltage has electrical-potential dimensions while Planck length has distance dimensions. No direct physical voltage-to-Planck-length scaling law follows from the cipher. No external-universe simulation proof. Lean formal draft not machine checked.

Next gate: specify a gauge-invariant voltage geometry (potential difference, charged species, coherent reference, length/time boundary, electrode layout) and an independently testable wavelength/phase prediction.
