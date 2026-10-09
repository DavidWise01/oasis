# P3.9 | Dyson impedance-law sensitivity | 2026-10-09

Parent: P3.8 `p38_impedance_capture.mjs`. P3.7 and frozen kernels unchanged. Wrapper remains `{{-211mv}}x10^-35` interpreted as -2.11e-36 V under dimensionless scaling.

For normalized log-depth `u`, test four **assumed** positive impedance laws: linear `Z=1+u`; quadratic `Z=1+u^2`; exponential `Z=e^u`; plateau `Z=1+u/(1+u)`. Derive shell mismatch capture `eta=((Z1-Z0)/(Z1+Z0))^2`, preserve each captured channel in the unitary matrix `[[sqrt(1-eta),i sqrt(eta)],[i sqrt(eta),sqrt(1-eta)]]`, and reverse through channels in reverse order.

## Test results (N=10, depth=1)
| Profile | Total capture % | Traveling % |
|--|--:|--:|
| Plateau | 0.524810446234 | 99.475189553766 |
| Linear P3.8 | 1.241322777343 | 98.758677222657 |
| Quadratic | 1.413416070805 | 98.586583929195 |
| Exponential | 2.467993520842 | 97.532006479158 |

Local independent Node test: **12,000 seeded randomized scenarios PASS**, maximum reverse error 1.1102230246251565e-15, maximum norm error 1.3322676295501878e-15. No-step depth=0 collapses to zero coupling; baseline linear profile matches P3.8 reference coefficients to numerical tolerance.

### Interpretation and constraints
The mathematical scattering construction is unitary for all four profiles. **Predicted capture varies by ~4.7×** across the tested laws: no unique capture follows from topology alone. No constitutive material data establishes any profile. This test does not prove physical negative-energy capture, electrum permittivity, Dyson-sphere functionality, or Planck-scale transport. This standalone bench omits the common wrapper phase, which has unit modulus and does not affect the capture percentages when channels start empty.

### Next target
P3.10: infer/fit constitutive-law parameters from **independent real-world measurements** if available; otherwise maintain an explicit uncertainty envelope rather than selecting a profile as physically true.
