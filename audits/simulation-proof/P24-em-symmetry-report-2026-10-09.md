# ROOT0 P2.4 — eight-state photon, conservation, Maxwell transversality and isotropy

**2026-10-09.** Frozen source unmodified; executable PASS; formal Lean draft **not compiled**; physical simulation theory **not proven**.

## Original evidence versus added assumptions

The byte-pinned `AE Generative-First Frozen Kernel v92` has a 12-cubit logical phase cycle, identity/generation/append-only lineage, photon naming, vector/voxel/vogel symbols and no Maxwell gauge field or calibrated SI-position transport. Canon SHA-256 `8f2be8951098c7e1764c3c0f5bba982fb3fd8c71f094924b79d0172a313a7bf8`; original Git blob `bf84cfc8746ccaf35c0204050ada8c3980817cb8`. Its canon explicitly disclaims physical claims without separate validation.

**P2.4's supplementary hypothesis H₈** interprets `2^3` as eight *literal classical* directional velocities, `n=(±1,±1,±1)/√3`, all with equal step speed. The frozen ROOT0 rules do **not** require this interpretation. In particular a photon could carry an eight-state internal register without moving only in eight directions. All no-go statements below apply only to H₈.

## Exact algebraic gate

For uniform classical corner directions, every odd coordinate moment vanishes and the covariance is `E[n_i n_j] = δ_ij/3`. Therefore H₈ passes **second-order isotropy**.

Fourth-order statistics reveal a rigid anisotropy. Each corner independently has `n_x^4 = n_x² n_y² = 1/9`. Consequently, for **any** real weights `w_b` summing to one,

`E_w[n_x^4] = E_w[n_x² n_y²] = (Σ_b w_b)/9 = 1/9`.

For exact SO(3)-isotropic unit directions, `E[n_x^4]=1/5` and `E[n_x² n_y²]=1/15` (the isotropic tensor ratio must be 3:1). Thus **no classical reweighting of only those eight literal directions can restore fourth-order isotropy**. This does not rule out emergent, quantum, or continuum transport.

The direction-resolved fourth moment `F(e)=E[(n·e)^4]` equals `1/9` for a coordinate axis and `7/27` for a body diagonal; angular contrast is `4/27`. A 45° spatial rotation maps an eight-corner vector outside the discrete set, independently establishing that its finite support is not exactly SO(3)-closed.

## Electromagnetic compatibility gate

For each normalized corner n, construct transverse projector `P=I−nnᵀ`. The test verifies `P²=P`, `Pn=0`, `trace(P)=2`, and finds explicit real orthonormal polarization vectors `u,v` such that `P=uuᵀ+vvᵀ`. For the eight uniform directions, the average projector is `(2/3)I`; transversality and second-order rotationally averaged polarization **pass**.

The identity and cyclic eight-state *permutation* direction-update operators preserve the ℓ² norm of any complex eight-amplitude state. 512 deterministic random amplitude trials PASS. This establishes norm conservation for these toy maps **only**, not Maxwell-energy conservation, quantum field gauge invariance, Maxwell equations, or a photon dispersion law.

## Dimensionful but still conditional discriminator

Independently import the **added** 3D centered-difference *scalar wave* from P2.0 with `τ=l_P/c`, `a=2l_P`, which is strictly below its stability CFL limit `3(cτ/a)²=0.75<1`. The model's leading small-k group-speed correction depends on the fourth angular harmonic `S₄(e)=Σ_i e_i⁴`. For illustrative flat-space `D=1 Gpc`, photon energies 30 versus 1 GeV:

- Cubic-axis delay `2.3279177100660055e−19 s`;
- Body-diagonal delay `2.586575233406673e−20 s`;
- Difference `2.0692601867253383e−19 s`;
- 1 ms timing resolution is a factor `4.83e15` coarser than this angular contrast.

The wave model **is scalar, not Maxwell**. It is not mathematically derived from the eight-state transport, the original I13 state witness, or frozen AE-v92. The angular contrast is an illustration of a potential observation protocol, NOT a parameter-free ROOT0 prediction or an analyzed astronomical observation. Angular source orientation, redshift, intrinsic emission lags, detector noise and gauge dynamics would all require specification before preregistration.

**Normalization correction:** signed component steps `(±1,±1,±1)` have Euclidean length √3. If total step length is externally set to `l_P`, each coordinate step must be `±l_P/√3`; the physical speed is then `l_P/τ=c`. Counting raw components as one Planck length each would instead give √3 c. This corrects a potential confusion in the earlier P2.3 visual explanation.

## Execution and proof ledger

`python p24_em_symmetry_test.py` pins both original files, advances frozen v92 for **12,288** logical steps (1,024 cycles), checks exact rational moments, 512 rational weight examples, eight explicit transverse polarization pairs, 512 complex amplitude permutations, direction rotations and conditional dispersion contrasts.

**PASS:** source/canon verification; exact first and second angular moments; strong weighted fourth-moment obstruction; 8 transverse-polarization projector identities; amplitude-norm conservation of tested permutations; 12,288 frozen transitions; conditional dispersion formulas.

**NOT ESTABLISHED:** a unique ROOT0 physical direction rule, Maxwell gauge covariance or exact Lorentz invariance, a quantifiable ROOT0-specific empirical photon prediction, an external experimental test, or simulation theory. **Lean draft uncompiled**; executable exact rational Python is evidence of the finite algebra only.

## Next gate P2.5

Test a two-polarization, gauge-covariant emergent field model that could escape the classical eight-direction angular obstruction; require the model's Hamiltonian/evolution to be derived and fixed *before* fitting a physical observation. Otherwise record the absence of a unique physical embedding as a continuing proof barrier.
