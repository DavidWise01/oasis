# ROOT0 P2.2 — Proven logical clock; physical observation map remains uncalibrated

**Status:** 2026-10-08. Actual frozen AE Generative-First v92 source reused without modification; independent reachability test passed over 12,288 `advance()` operations; Lean draft NOT machine checked; physical simulation hypothesis OPEN.

## Verified source of truth

- Git `DavidWise01/oasis/kernel/frozen/ae-generative-first-v92/kernel.py` Git blob `bf84cfc8746ccaf35c0204050ada8c3980817cb8`; raw source SHA-256 `77fb69e9efda9a4f87e1c221aaa46680d68f6196e8440b83bf8e65d69d0d1d6f`.
- Original immutable `CANON.json` SHA-256 `8f2be8951098c7e1764c3c0f5bba982fb3fd8c71f094924b79d0172a313a7bf8`.
- The actual `Context` fields are `identity,generation,q,token,v3,parent_seal,lineage_seal`. The actual `V3` fields are `vector,voxel,vogel,sg`, each a derived string or digest-derived label, not SI-coordinate vectors.
- The source's `PHOTON` and `PHOTON_BIRTH` values are named literals; `PHOTON_BIRTH` enters the seed at wraparound. No operator in `advance(ctx)` carries an electromagnetic field or a physical coordinate.

## P2.2 Theorem 1: SOURCE-DEFINED DIMENSIONLESS LOGICAL CLOCK

Let `q∈{0,...,11}` be the phase, and `g∈N` the generation. Define `n=12*g+q`.

- If `q<11`, the source `advance` assigns `(q',g')=(q+1,g)`. Then `12g'+q'=12g+q+1`.
- If `q=11`, `advance` assigns `(q',g')=(0,g+1)`. Then `12g'+q'=12(g+1)=12g+11+1`.

Thus **for genesis-reachable states** `n(advance(s))=n(s)+1`. This is an exact algebraic consequence of the original implementation. Its physical units are **none**; a physical time map `t(s)=τ n(s)` additionally requires a calibrated `τ` in seconds.

The exhaustive executed regression checked 12,288 calls (1,024 wraparounds) and 12,288 parent seals, with `12,289` reachable states and zero logical-clock failures.

## P2.2 Theorem 2: NO UNBOUNDED NONZERO VELOCITY FROM PHASE ALONE

For any observation function `f(q)` (position vector, scalar, or label) depending only on phase, `q(n+12)=q(n)`, hence `f(q(n+12))=f(q(n))`. If the same observable were a ballistic physical position with constant nonzero step `d`, it would satisfy `x(n+12)=x(n)+12d`, contradiction in ordinary torsion-free physical coordinates. Therefore `d=0`. This is independent of the shape of `f` and is not specific to a sampled example. Retaining `g` or another growing transport register is necessary for unbounded position under this class of observation map.

The executable test checked three different phase-observation functions at every available 12-step pair. The Lean draft formalizes this integer-valued no-go with an explicit 12-step telescoping proof, but awaits Lean compiler confirmation.

## Boundary adversary: forged/unreachable `Context` objects

The Python `advance` function does not validate arbitrary supplied `Context.q`. Cases `q=-2,-1,12,13,23` were constructed with Python's `dataclasses.replace`. Their next-step `12g+q` changed by `+13,+13,-11,-11,-11`, not +1. This is a validity boundary: **the theorem applies to the reachable domain or to an explicit phase type `Fin 12`, not arbitrary unchecked Python `Context` input**. This finding is not a failure of normal `run_steps`, which starts from verified genesis.

## P2.2 Constructive nonuniqueness of physical calibration

Both of the following proposed embeddings yield the identical original symbolic lineage:
- A: `t_A=τ n`, `x_A=a n e_x`;
- B: `t_B=2τ n`, `x_B=3a n e_y`.

`τ` and `a` are external unit scales. The original `advance` does not read or constrain them. These simple examples are **not asserted to be physical photons**; they are countermodels showing that the exact source cannot uniquely determine coordinate units/directions without bridge axioms. If an additional photon axiom enforces `speed=c`, that constrains `a/τ` but **does not uniquely establish 3D Maxwell dynamics, physical orientation, cosmology or external simulation**. The source needs an explicit observation function with physically calibrated dimensions and an observable tied to actual measurements.

## Falsifiability and win condition

No verified physical light-speed deviation was derived. P2.0's auxiliary 3D scalar-wave dispersion cannot be imported into v92 by analogy; P2.1 already proved multiple equally valid couplings to it. The next meaningful advance is to specify an independent *physical bridge axiom* (e.g. an electromagnetic-field state, signed propagation operator and geometric coordinates), demonstrate source refinement in a machine-checkable form, and preregister a measurable observable with a conventional-physics null model. An `x=an` assertion alone is a choice of external interpretation, not a prediction of the frozen kernel.

Source-local model consistency is established. Proof that **our physical universe** is simulated remains unestablished.