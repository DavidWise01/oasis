# P3.8 — deterministic Dyson-shell impedance law (2026-10-09)

**Status:** mathematical simulation / locally bench-tested, not a physical validation.
**Parent:** P3.7 `p37_dyson_scale.mjs`; previous modules and frozen kernels remain untouched.
**Preserved wrapper:** `{{-211mv}}x10^-35`, yielding `-2.11e-36 V` when the multiplier is dimensionless.

## Derived model coefficients
Define normalized logarithmic depth `u = ln(r0/r)/ln(r0/rPlanck)`. For shell j among N and configured depth d, its endpoints are `u0 = d*j/N` and `u1 = d*(j+1)/N`. Introduce the **assumed**, dimensionless impedance profile `Z(u)=1+u`. Its Fresnel-inspired mismatch produces `eta_j = ((Z1-Z0)/(Z1+Z0))^2`. Thus eta is determined without a free capture slider **conditional on the selected impedance profile**. The profile itself is not measured, uniquely implied by the user's notation, or demonstrated to represent electrum, vacuum, or an astrophysical Dyson sphere.

For each shell retain the old two-channel unitary operator `U_eta = [[sqrt(1-eta), i sqrt(eta)], [i sqrt(eta), sqrt(1-eta)]]`. The reverse applies its Hermitian conjugate in reverse shell order, with the old P3.7 voltage-derived phase distributed once across the wrapper. Captured channels remain available for reversible replay; true dissipative capture would require explicit environmental dynamics.

## Local validation
Node.js v22.16.0 tests: **12,000 randomized cases passed**, including arbitrary complex initial channels. Maximum initialized-state recovery error `1.1102230246251565e-15`; maximum norm error `1.3322676295501878e-15`; maximum analytic power error `1.2212453270876722e-15`. At N=10 and depth=1: eta1 `0.0022675736961451282`, eta10 `0.0006574621959237356`, traveling norm `0.9875867722265661`, captured norm `0.0124132277734339`. At depth=0 all eta are zero.

**Validation qualification:** the local test ran with a hand-transcribed, API-compatible subset of the P3.7 dependency because the runtime cannot download GitHub raw files. The source/module and test are committed to GitHub, but independent execution against the exact repository P3.7 dependency and remote CI have not yet been verified.

## Model boundaries
A dimensionless voltage multiplier does not turn voltage into length. The Planck radius remains an independent display coordinate. `Z(u)` is an illustrative impedance assumption, not a derived physical law. No measured optical constants, negative-energy Dysons, Planck-scale transport, or quantum-gravity predictions follow from these calculations.

## Next target
P3.9 should conduct constitutive-law sensitivity testing: compare multiple explicit impedance profiles, quantify capture sensitivity, and identify observations required to discriminate among them. Treat `Z(u)=1+u` as a transparent baseline, not a uniquely validated capture law.
