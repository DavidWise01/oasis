# ROOT0 P3.3 — Signed voltage boundary: physical wavelength/phase identifiability

**Date:** 2026-10-09. **Status:** CONDITIONAL PHYSICS EXAMPLES PASS / UNIQUE ROOT0 PREDICTION FAILS / REALITY-SIMULATION UNPROVEN.

## 1. Source and carried context

The user-defined symbolic system contains two 10,000-address silos, 100 million composite tensor addresses, pinned `Complex[0]`, a signed `{-e{ ..||..|....||| }+e}` phase carrier, an operational 208-forward + 208-mirrored-inverse cycle, and a **black wrapper potential of `-211 mV`** around the orange wavelength/amplitude visualization. Previously committed P3.2 source is copied untouched into `upstream/`; this P3.3 work introduces physical comparison models separately. No source-level derivation of SI quantities from 208 cipher states has been provided.

## 2. Model A — uniform potential without a field

The voltage `V=-0.211 V` as a constant **absolute scalar potential**, i.e. with no spatial gradient and no changing vector potential, produces `E=-grad phi - partial_t A=0` and `B=0`. The electromagnetic potentials have a gauge symmetry `phi' = phi - partial_t chi`, `A'=A+grad chi`. A spatially uniform offset of `phi` can be removed by an appropriate time-dependent `chi` without changing E and B. Therefore it cannot by itself cause a gauge-invariant optical phase, frequency shift, or wavelength shift for a neutral free photon. The charged-port reference `qVt/hbar` computed in P3.2 is not automatically an observable photon phase; it is a gauge-dependent convention unless a complete coherent comparison loop and appropriate charged degrees of freedom are specified.

The executable verifies this gauge invariance explicitly with 24,000 pseudorandom affine potential/gauge representatives. The analytic proof is immediate:

`E' = -(phi_x - chi_tx) - (A_t + chi_xt) = -phi_x - A_t = E`.

The implementation is a simplified 1D affine representative (`chi(x,t)=u*x*t+v*t+w*x`); it is an exact identity of those field derivatives, not a proof of gauge invariance for every possible electrodynamic field configuration.

## 3. Model B — difference across a material

A separate *potential difference* `Delta V=-0.211V` across idealized electrodes separated by `d` yields `E=Delta V/d`, assuming a uniform field over the optical mode. In a non-centrosymmetric material with effective electro-optic coefficient `r` and overlap `Gamma`, conventional first-order Pockels response:

`delta_n = -(1/2) n^3 r Gamma E`.

At fixed source frequency and free-space wavelength `lambda0`, a wave crossing a length `L` acquires:

`delta_phi = (2pi L / lambda0) delta_n = -(pi/ lambda0) n^3 r Gamma (Delta V/d) L`.

For the illustrative inputs `d=10um`, `L=10mm`, `lambda0=600nm`, `n=2.2`, `r=30pm/V`, `Gamma=1`:

- `E=-21,100 V/m`;
- `delta_n=+3.370092e-6`;
- `delta_phi=+0.3529152089707245 rad`;
- `lambda_medium_before=272.727272727 nm`;
- `delta(lambda_medium)=-0.4177793600 pm`;
- `delta(lambda_vacuum)=0`: a static medium does not independently upconvert or downconvert the source frequency;
- with interferometer bias `pi/2`, visibility `0.8`, `I/I0=0.5[1+0.8*cos(pi/2+delta_phi)]` changes from `0.5` to `0.36174607428469946` (difference `-0.13825392571530054`).

These are **calculated, not measured** values. Real results additionally require tensor component/polarization orientation, crystal cut, mode overlap, dispersion, losses, stability, waveguide geometry, detector calibration, etc.

## 4. No unique ROOT0 prediction

Models A and B both accept the exact same `-211 mV` labeled wrapper and unchanged 208-state cipher, yet yield different optical phases `0` vs `+0.352915...rad`. More generally, material coefficient `r=0` gives null while nonzero `r` gives a material response; varying `d`, `L`, `Gamma`, `lambda0` continuously varies `delta_phi` with no alteration of cipher state. This is a **constructive non-identifiability witness**. To claim a novel ROOT0 prediction, the kernel must uniquely specify additional physical variables and a gauge-invariant observable *before* any comparison with measurements, not merely fit a positive effect after it is seen.

A distinction from P3.2: the 0.211 eV charged-port magnitude converted into a notional photon wavelength (~5.876 um) is an **energy equivalence**; it does not imply that a photon in the actual field has acquired that energy. Likewise the Planck `1.616255e-35m` zoom endpoint is a display coordinate. `|V|/l_P` has electric-field dimensions, and extrapolating a small-signal Pockels coefficient or macroscopic field model to such scales is unjustified.

## 5. Falsifiable *conventional* optical experiment

For a physically constructed two-arm interferometer with a controlled non-centrosymmetric electro-optic element on one arm, drive the electrodes `+/- 0.211V` across measured `d=10um`. Preregister `n`, effective `r`, overlap `Gamma`, `L`, source wavelength and polarization from independent calibration. Measure balanced phase/interference against applied voltage while simultaneously running a no-material/no-field null. The elementary conventional prediction for the chosen idealized parameters is `delta_phi(−211mV)=+0.3529152rad`; voltage sign flip reverses the phase; doubling electrode separation halves it; removing effective electro-optic coupling eliminates the effect. Instrument uncertainties must be included for a real experiment. None of these predictions discriminates simulation theory; they are textbook electrodynamics and material response.

## 6. Tests and artifacts

Executed `node test_p33.mjs` (24,000 randomized gauge transformations, dimensional/model scaling, zero controls, invalid-value tests and one complete earlier P3.2 208+208 inverse cycle). All PASS. Executed Chromium with tested self-contained `standalone.html`, controls `Reset`, `Reverse voltage`, `Material null`, `Verify formulas`, `Planck reference`, `Gap x2` all PASS and no JavaScript errors. Local modular files syntax-check with Node; the local HTTP browser route was blocked, so hosted GitHub Pages publication can only be considered *source available*, not independently confirmed deployed. Formal Lean statement is a draft, uncompiled. A sha256-indexed ZIP package preserves evidence; `README.md` provides reproduction.

## References

- R. A. Minasian, *Encyclopedia of Modern Optics*, Pockels electro-optic effect equation https://www.sciencedirect.com/topics/chemistry/pockels-effect
- University of Delaware, *Electro-optic Modulator Fundamentals*, equations (2.1-2.3): https://udspace.udel.edu/server/api/core/bitstreams/a574369c-1d1c-4a21-a674-e74b09068f6a/content
- R. M. Mathis et al., *Enhancing Pockels effect in strained silicon waveguides*, Optics Express 27 (2019): https://opg.optica.org/oe/fulltext.cfm?uri=oe-27-19-26882

**Next proof gate P3.4:** postulate a *distinctive nonstandard, gauge-invariant* coupling derived from original ROOT0 state transitions without choosing free post hoc parameters. If this cannot be supplied, report underdetermination as a formal limitation rather than invent a physical effect.