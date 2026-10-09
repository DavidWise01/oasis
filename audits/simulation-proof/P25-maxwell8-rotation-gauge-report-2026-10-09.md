# ROOT0 P2.5 — Eight internal amplitudes and electromagnetic symmetry

Status: CONSTRUCTIVE MODEL-LOCAL PASS / EXTERNAL REALITY UNPROVEN. Date: 2026-10-09.

## Source provenance and scope

The exact, unmodified frozen v92 kernel and canon are included with this package. Git blob of `kernel.py`: `bf84cfc8746ccaf35c0204050ada8c3980817cb8`. SHA256 of `CANON.json`: `8f2be8951098c7e1764c3c0f5bba982fb3fd8c71f094924b79d0172a313a7bf8`. The immutable canon expressly describes a symbolic/isomorphic simulation model and does not assert a physical derivation. The executable source was not modified. The appended electromagnetic structure below is a **candidate physical interpretation**, not a logical consequence of the frozen kernel. In particular, eight discrete classical symbols do not by themselves supply a complex 8-dimensional amplitude Hilbert space or quantum superposition; that structure is independently introduced here.

## Explicit construction

Let ψ(k)=(E_x,E_y,E_z,B_x,B_y,B_z,s_0,s_1) ∈ C⁸ for nonzero continuum wavevector k. The final two scalar slots are inert spectator/auxiliary components, not physical photon polarizations. Set n=k/|k| and `K(n) v = n × v`. Define the Hermitian 8×8 matrix

```
Q(n) = [ 0   K    0 ]
       [-K   0    0 ]
       [ 0   0    0₂]
```

where each top block is 3×3, with K real skew-symmetric. Since K² = nnᵀ-I₃, Q²=diag(I₃-nnᵀ, I₃-nnᵀ,0₂), Q³=Q. Hence the exact Maxwell-style Fourier propagator at frequency ω=c|k| can be written

`U(k,t)=exp(iωt Q)=I₈+i sin(ωt) Q+[cos(ωt)-1]Q²`.

- **Unitarity / norm:** Q†=Q, so U†U=I; `||ψ||²=||E||²+||B||²+|s₀|²+|s₁|²` is conserved. This is a mathematical quadratic norm; matching physical electromagnetic energy requires additional normalization/interpretation.
- **Transverse Gauss constraints:** `k·E` and `k·B` remain constant, since k·(k×v)=0. If zero initially, remain zero. The longitudinal E/B modes and auxiliary scalars are zero-frequency spectators.
- **Exactly two positive-frequency modes:** Q has eigenvalues (-1,-1,0,0,0,0,+1,+1). On the eigenvalue -1 subspace, U contributes `exp(-iωt)`. Given any transverse orthonormal e1,e2, the modes `(e_i, n×e_i,0,0)/sqrt(2)` span the two-dimensional positive-frequency subspace. That is a *classical Fourier wave-polarization* count; no photons have been quantized here.
- **Rotational covariance:** for proper R∈SO(3), D(R)=diag(R,R,1,1), and K(Rn)=R K(n) Rᵀ imply Q(Rk)=D(R)Q(k)D(R)†; hence U(Rk,t)=D(R)U(k,t)D(R)†. Under improper R with det(R)=-1, treat magnetic B as **axial** with D(R)=diag(R,det(R)R,1,1); the same covariance holds. Unlike the previous literal eight cube-corner directions, the amplitude basis is not limited to 8 spatial axes.
- **Gauge consistency of field observables:** for A→A+i k χ, ∂ₜ A→∂ₜ A+i k ∂ₜχ, φ→φ−∂ₜχ, then E=−∂ₜ A−ikφ and B=ik×A are unchanged. This checks invariance of classical fields under gauge-potential redundancy, not a quantized gauge-field action nor lattice gauge invariance.
- **Clock independence:** 12,288 exact `kernel.advance` transitions (1,024 complete 12-phase generations) run with identical source states and seals regardless of the externally attached propagator.

## Executed adversarial tests

512 pseudorandom orientations, transverse bases, complex field values, times, gauge potentials, proper rotations and improper reflections were tested. All maximum numerical residuals below 3e-14; group composition, projector rank, transversality, gauge invariance, parity and both physical modes passed. Negative controls intentionally inserted nonunitary scaling, a unitary but rotation-breaking phase, and longitudinal leakage; all were correctly detected. Exact kernel/canon hashes passed.

## Discriminating-physics underdetermination

Define a family of rotationally invariant phase laws `ω_α(k)=c|k|[1+α(k l_P)²]`, `α=0` (standard Maxwell vacuum wave) or `α=−1` (modified dispersion, only intended in low-k regime). Each uses the same Q and its unitary transverse propagator; isotropy, transverse constraints and norm conservation remain intact. They differ in group speed: `v_g/c=1+3α(k l_P)²`. Neither α nor complex-amplitude interpretation is present in frozen v92.

Under the **illustrative flat-space** assumptions `D=1 Gpc`, 30 GeV versus 1 GeV, `l_P=1.616255e−35 m`, `ħc=0.1973269804e−15 GeV m`, the delay (high minus low photon) is 0 s for α=0, and ~1.8623341681e−18 s for α=−1. The latter is not a prediction of ordinary Maxwell vacuum dynamics. Source-emission delay, cosmology, quantum noise, experimental instrument resolution and external validation remain unspecified. Both models obey our limited symmetry/unitarity tests; only α=0 exactly obeys the unmodified Maxwell dispersion law. Enforcing Maxwell vacuum as an exact axiom therefore selects no novel ROOT0 physical effect.

## Main proof outcome

**P2.4's literal eight-direction fourth-moment obstruction does not imply an eight-component carrier cannot be rotationally covariant.** This explicit 3+3+1+1 complex representation supplies an SO(3)-covariant continuum classical Maxwell-like field with two positive-frequency transverse polarizations, while the ROOT0 v92 symbolic transition remains unchanged. This does not prove the frozen kernel produces this representation, Maxwell dynamics, spacetime, photons, or a simulated reality.

**Next proof gate P2.6:** A typed, dynamically testable map from the frozen 12-phase/8-register kernel into a complex 8-component field and a uniquely specified `k`-space Hamiltonian. It must respect lineage, composition, gauge constraints, physical symmetries and prevent fitting dispersion after observation. Derive a preregisterable nonzero physical observable with uncertainties and a conventional null, or record that no unique prediction follows.