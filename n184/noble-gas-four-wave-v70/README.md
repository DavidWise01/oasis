# N184 — Noble-gas four-wave confluence v7.0

**Status:** additive symbolic/optical-wave simulation; not an experimental observation. Keeps frozen N184 60 × 40, OASIS main-aligned, and other baselines unchanged.

- Open UI: [index.html](./index.html) — linked from [N184 Four-Brace Confluence v4.1](../integration-v41/)
- Engine: [four_wave_model.mjs](./four_wave_model.mjs)
- Deterministic checks: `node test_four_wave.mjs`
- CI: `.github/workflows/n184-noble-four-wave-v70.yml`

## Symbolic target

Four incident ports meet at center zero within the N184 `+-{0}+-` brace. The optical field is displayed with a schematic electrum (Au+Ag) shell and an Ice IX core. A **user-proposed symbolic formulation** is `99 Ice IX + 0.33 O + 0.33 H + 0.33 N + 0.01 K`, with unspecified normalization, chemical form, pressure, and temperature. This is **not** a validated stoichiometric formula. Elemental potassium and potassium ions are chemically different; do not attempt to mix potassium metal with ice or water.

## Source optical lines

All four wavelengths are *representative* neutral-atom emission lines, not a full emission spectrum or intensity measurement:

| Port | Species | Approx. wavelength (nm) | Role |
|---|---|---:|---|
| W1 | He I, Z=2 | 587.56148 | first input |
| W2 | Ne I, Z=10 | 585.24878 | second input |
| W3 | Ar I, Z=18 | 696.5431 | third input |
| W4 | Kr I, Z=36 | 760.15457 | **alternative** independent fourth input |

Sources: [NIST helium](https://physics.nist.gov/PhysRefData/Handbook/Tables/heliumtable2.htm), [NIST Atomic Spectra Database](https://physics.nist.gov/asd), [NIST argon](https://physics.nist.gov/PhysRefData/Handbook/Tables/argontable2.htm), [NIST krypton](https://physics.nist.gov/PhysRefData/Handbook/Tables/kryptontable2.htm).

## Inverse and fourth noble gas are different choices

The **synthesized fourth port** is engineered as a three-frequency waveform, with the components directed from the fourth side:

```text
E4(center,t) = -[EHe(center,t) + ENe(center,t) + EAr(center,t)]
Etotal(center,t) = 0
```

That exact cancellation is a consequence of the model's phase/amplitude definition, **not** a discovery or a measured physical property. The reinforcement mode switches the negative sign to positive and therefore doubles the three-input center amplitude. A single-frequency Kr I line does not perfectly cancel the sum of three different frequencies over time.

Spatially the inverse is launched from a different direction, so cancellation occurs at the center point only, not over the whole space. Reflection is a common scalar attenuation factor, **not** a gold-silver thin-film solution. The core polarization is a dimensionless damped oscillator, **not** a realistic Ice IX constitutive law.

## Explicit boundaries

- `184` refers to an N184 symbolic address/target, **not** to a verified element 184, nor directly to 184 neutron shell filling.
- Ice IX stability requires a suitable high-pressure thermodynamic regime; none is computed here.
- No claims of Planck-scale cavities, gravitational-wave storage, dark-matter generation, energy creation, radiation trapping, or real radiation exposure.
- For physical follow-up, measure optical reflectance/transmittance and pressure-dependent dielectric response before replacing the toy coefficients.

## Regression scope

The CI checks 11 deterministic properties: gas anchors, ideal inverse node, reinforcement, Kr mismatch, phase detuning, full reflection, zero drive, off-center residual, zero oscillator response, determinism/finite values, and parameter rejection. **Passing these verifies software consistency only.**
