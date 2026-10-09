# ROOT0 P2.1 — Source-pinned physical-calibration nonuniqueness

**2026-10-08 · Executable PASS · Full source and frozen canon verified · Lean UNCOMPILED · Simulation theory NOT PROVEN.**

## Proof target

Does the **actual frozen AE Generative-First Kernel v92**, combined with the extra hypothesis that one transition lasts one Planck time, imply **one unique metric lattice spacing or photon propagation delay**? **No, for the implemented transition with the additional scalar wave bridge used in P2.0.** This is a constructive underdetermination result, not a proof that simulation theory is true or false.

## Authentic source and control

Original GitHub `DavidWise01/oasis/kernel/frozen/ae-generative-first-v92/`:

- `kernel.py`: exact original Git blob **`bf84cfc8746ccaf35c0204050ada8c3980817cb8`**; local Git hash-object matched.
- `CANON.json`: exact original SHA-256 **`8f2be8951098c7e1764c3c0f5bba982fb3fd8c71f094924b79d0172a313a7bf8`**; original `load_and_verify_canon()` passed.
- The canon defines a symbolic/isomorphic model and explicitly lists `physical_claim: none; symbolic/model-local unless separately validated`.
- `advance(ctx)` computes next q/token, identity, v³, generation and SHA lineage from the previous symbolic context and canon digest. It contains no numeric metric distance, physical dimension, wave field, electromagnetic coupling, energy or laboratory observable. The AST audit confirmed no spatial-pitch parameter is passed to the transition.

## Two competing physically calibrated models

Keep exact frozen `genesis()/advance()` unchanged and its full canon. As a **separate, proposed physical embedding**, assume one tick `τ=t_P=ℓ_P/c`, and impose the 3D finite-difference *scalar*, not Maxwell, wave equation introduced as a candidate in P2.0. Its CFL condition is `3(cτ/a)² < 1` for strict stability.

- Model A: `a = 2 ℓ_P` ⇒ `r=1/2`, `3r²=3/4` (strictly stable).
- Model B: `a = 3 ℓ_P` ⇒ `r=1/3`, `3r²=1/3` (strictly stable).

Both worlds execute exactly the same **4,096 transitions** of source-pinned AE v92. Full state/lineage receipt SHA-256 is identical and all existing invariants pass, since no `a` enters the original kernel.

However the added scalar wave predicts different leading-order propagation corrections. For `E_H=30 GeV`, `E_L=1 GeV`, and `D=1 Gpc` *in a flat-space illustrative path*,

`Δt(n,a) ≈ (D/c) [(E_H²−E_L²) / (8(ℏ c)²)] × [ a²∑n_i⁴ − (cτ)² ]`.

Results:

| Attachment | Axis delay (s) | Body diagonal (s) |
|---|---:|---:|
| `a=2ℓ_P` | `2.327917710066006e−19` | `2.5865752334066726e−20` |
| `a=3ℓ_P` | `6.207780560176014e−19` | `1.5519451400440035e−19` |

Thus `Δt_B(axis)/Δt_A(axis)=8/3` and `Δt_B(diagonal)/Δt_A(diagonal)=6`, despite **identical frozen v92 states and lineage seals**.

## Mathematical countermodel

Let `S` be v92 contexts and `T:S→S` be the actual frozen `advance`. Define `F_a:S×{a}→S×{a}` by `F_a(s,a)=(T(s),a)`. For any two `a` and `b`, 

`π_S(F_a^n(s,a)) = π_S(F_b^n(s,b)) = T^n(s)`.

But the auxiliary observation maps `O_a` and `O_b` assign different dimensionful travel delays. Hence a single unique photon-delay formula is **not entailed by the implemented symbolic transition plus a fixed tick alone**. This conclusion is conditional on the stated interface: unspecified extra geometric constraints could in principle select one embedding.

This is a non-identifiability / model-completion obstruction, not a theorem about the external universe. A symbolic model matching a physical theory does not establish that external reality runs it.

## Tests and limits

- Exact original kernel Git blob: PASS.
- Frozen `CANON.json` SHA and `load_and_verify_canon`: PASS; corrupted-canon negative control rejected.
- Both independent 4,096-transition runs, identity wrap and lineage invariants: PASS.
- Identical 4,097-state trajectory digest across physical calibrations: PASS.
- Distinct scalar-wave axis/diagonal delays, and exact 8/3 and 6 ratios: PASS.
- Six additional strictly stable spatial spacings demonstrate continuous parameter freedom.
- Lean source expresses abstract conditional countermodels but has **not been compiled**. It is not a proof linking v92 to photons.
- The actual Maxwell/QED field, causal cones, orientation, cosmological redshift, laboratory measurement bridge and a source of physical SI units remain unspecified.

## Next proof gate P2.2

**Derive or explicitly postulate an independently justified operational observation map** from `(q, identity, v³, photon label, toroidal `|||` seam)` to a wave/field state and physical `(x,t)` in meters/seconds, with a **single predeclared pitch and time mapping**, and prove transition-refinement (`E∘T=U∘E`). If no such map can be grounded in the frozen rules, report a missing axiom instead of claiming parameter-free physics.

This report is not an invention-priority or name-lineage audit. ROOT0's win condition remains a mathematical and empirical theory of simulated reality, and is **not yet established**.