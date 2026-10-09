# ROOT0 P2.6 — Eight discrete register labels versus eight continuous Maxwell-field amplitudes

**Executed:** 2026-10-09. **Gate:** PASS — *classical encoding no-go and conditional quantum/complex lift*. **Physical simulation hypothesis:** still unproven. **Lean:** draft only; compiler not installed.

## 1. Source-pinned kernel and what is actually implemented

The original and unchanged AE v92 `kernel.py` is verified against Git blob `bf84cfc8746ccaf35c0204050ada8c3980817cb8`, and `CANON.json` against SHA256 `8f2be8951098c7e1764c3c0f5bba982fb3fd8c71f094924b79d0172a313a7bf8`. The canon explicitly declares **no physical claim without separate validation**.

In source, `Context` fields are `identity,generation,q,token,v3,parent_seal,lineage_seal`. The executable v92 does **not** contain a typed photon-3-bit register or an actual 8-component complex amplitude. The proposed `2^3 = 8` state-carrier and the field map below are additional mathematical interpretations, not facts about the frozen v92 implementation. The original kernel ran **12,288 source transitions**, final `(generation,phase)=(1024,0)`, without deviation when different external field interpretations were considered.

## 2. The wrong identification and constructive encoding

There is a crucial type distinction:

- **Three classical bits:** the *set* `B = {0,1}^3`, with cardinality `|B|=8`. One realized register contains one of these eight values.
- **A coherent three-qubit state (NEW structure):** vector space `H=(C^2)⊗(C^2)⊗(C^2)≅C^8`, with **eight simultaneous complex coefficients**, subject to normalization and a global-phase equivalence for rays. Merely having eight classical states does not implement such superposition, interference, or entanglement.
- **The P2.5 Fourier field (NEW structure):** `F(k)=(E_x,E_y,E_z,B_x,B_y,B_z,s0,s1) ∈ C^8` with momentum `k` and Fourier-time generator `Q(k)`. A vector-space isomorphism to the qubit Hilbert space is mathematically available, but the physical interpretation and transition operator remain independent additional axioms.

The most immediate classical embedding is `e : B → C^8`, `e(b)=unit basis vector with coordinate b`. It is injective but not surjective. The real-valued onehot encoding selects only eight points from infinitely many amplitudes. Its complex-linear *extension* is bijective only after upgrading to `C^8` inputs and a linear quantum interpretation; the original 8-label mapping has no linear structure that would force this.

## 3. Exact finite-rotation no-go (no numerical fitting)

At a fixed reference wavevector `k=(0,0,1)`, take an electromagnetic field with `E=(1,0,0)` and all other components zero. Rotate the field around the z axis by `R_j = R_z(2πj/9)`, `j=0,...,8`, using the P2.5 block rotation `D(R)=diag(R,R,1,1)`. The nine field vectors are **pairwise distinct**, including as *rays modulo a global complex phase*. A map whose input has only eight classical labels cannot cover all nine; therefore **no exact label-only encoding can be closed under this nine-element subgroup while representing this nonzero transverse field**. The proof uses 9>8 and rotations of a nonzero transverse vector, not floating-point assumptions. Numeric checks found minimum pairwise field distance `0.68404028665`, and maximum overlap-squared of distinct rays `0.88302222156`.

More generally, suppose a set of at most eight classical images is closed under rotations `R_z(2π/9)` and `R_x(2π/9)`. Any field with a nonzero component transverse to z or x has an orbit of nine distinct field vectors and is impossible in that set. Closure under both rotations forces all E and B vector components to vanish. Only the scalar auxiliary components survive; these cannot represent transverse photon fields. This argument assumes **exact equivariant field-vector encoding**, not an approximate or emergent continuum limit. It also does not rule out a *larger continuous state alongside the classical register* or quantum amplitudes over the labels.

## 4. Failure of one-hot closure under the P2.5 Maxwell-like update

The external P2.5 operator is `Q(k) = [[0,K],[−K,0]] ⊕ 0₂`, with `K v = k_hat×v`, and `U(k,θ)=I+i sinθ Q+(cosθ−1) Q²`. At `k=e_z` and `θ=π/4`, `U` is unitary but sends onehot basis values `0,1,3,4` to coherent two-component states. The **best squared overlap** with any single basis state is **1/2** for each; no classical deterministic 8→8 update can reproduce the complex state exactly. The remaining four basis labels are invariant spectators at that k. This check is about one-hot encoding into the *added* P2.5 model, not a claim about nature.

Positive-frequency transverse physical projector `P_-=(Q²−Q)/2` has rank **2** at nonzero k; in the eight natural coordinate basis, its diagonal weights are `[1/2,1/2,0,1/2,1/2,0,0,0]`, so **no one-hot coordinate is itself a normalized physical positive-frequency photon polarization**. Explicit coherent modes `(E_x+B_y)/√2` and `(E_y−B_x)/√2` lie in the rank-2 subspace. Six other dimensions correspond to negative-frequency, longitudinal, or auxiliary modes at this k. This is classical Fourier-mode structure, not a quantized single-photon Hilbert-space proof.

## 5. Positive conditional result and adversarial checks

A mathematical `C^2⊗C^2⊗C^2 ≅ C^8` tensor-product identification exists if complex coefficients and quantum linearity are **added as axioms**. The benchmark used 512 random normalized three-qubit product states; maximum norm error was <1e-15. It confirmed `Q³=Q`, Hermitian/unitary propagation, physical projector rank=2, two coherent transverse modes, and original v92 clock/lineage separation. It also checked a nine-angle orbit with no collisions under ordinary or projective equivalence.

**Precise theorem obtained:** An 8-valued *classical* register alone cannot form an exact, rotation-covariant, one-hot Maxwell field of nonzero transverse vectors. A continuous complex-amplitude lift can be constructed, but this changes the state type and requires an independently justified momentum map, field dynamics and physical measurement rule.

## 6. Why this still cannot prove actual-world simulation

A classical discrete program can approximate continuum physics at finite experimental resolution. The theorem rules out one **specific exact embedding**, not digital physics, quantum cellular automata, emergent Lorentz symmetry, or simulation theory. No experimentally distinct photon dispersion is forced: P2.5 already provided two covariance/unitarity-compatible dispersion choices with different arrival delays while leaving v92 unchanged. An observational match to a freely tuned added law would not be unique evidence for simulation.

**Next P2.7 obligations:** (1) specify whether 2³ means *classical states* or *quantum basis with complex amplitudes*; (2) define a source-grounded amplitude/measurement rule that preserves lineage; (3) derive a fixed, not retrospectively tuned Hamiltonian and momentum/time calibration; (4) prove gauge and rotation constraints and produce a dimensionful falsifiable prediction; (5) independently reproduce real-world observations against conventional physics.

## Reproduction and integrity

Run `python p26_register_to_maxwell_test.py` in the included directory; source integrity is checked before calculations. The frozen files are never modified. `P26DiscreteToMaxwell.lean` is an abstract rational/integer toy lemma draft, **not machine checked**. The complete runnable package includes this report, source, canon, frozen regression, JSON results and integrity hashes.