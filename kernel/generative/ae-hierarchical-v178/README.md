# AE Hierarchical Generative Kernel v178

**Status:** `GENERATIVE / APPEND-ONLY / SEALED`

This is the executable descendant of the frozen **AE Generative-First Kernel v92**.

The frozen parent remains under:

```text
kernel/frozen/ae-generative-first-v92/
```

This package does **not** rewrite that parent. It verifies the frozen `CANON.json` SHA-256 before generation and emits deterministic child states append-only.

## Hierarchy

```text
0.s0.0
  ↓
plank {0,1}
  ↓
gradient {-1,0,+1} -> {n,n+1,n+2}
  ↓
10 × 10 field
  ↓
(-2,+3) walker
  ↓
. = 2^3{{-2,+3}} = |<.>|
  ↓
aa bb cc dd --++ dd cc bb aa
  ↓
10 disjoint 10-cell orbit classes
  ↓
10!/13/9/6/3/2/1/1 = 11200/13
  ↓
/0/0 = STOP
  ↓
- <-> +
```

## Generative behavior

A state is immutable once emitted. A child is derived from:

- the parent state ID and seal;
- the explicit event payload;
- lane label;
- gradient;
- control token;
- current 10×10 point;
- frozen v92 canon identity.

The runtime derives a deterministic child `state_id` and integrity `seal`.

`emit_state(...)` is append-only:

- identical re-emission is idempotent;
- an existing path with different bytes hard-fails;
- a halted `/0/0` state cannot generate children.

## The lane mapping is intentionally explicit

The mathematics produces exactly ten orbit classes. The symbolic hierarchy supplies exactly ten labels:

```text
aaL bbL ccL ddL ddR ccR bbR aaR plank0 plank1
```

But the sealed literals do not choose one of the `10!` label-to-orbit permutations.

Therefore the runtime accepts an optional **bijection** and validates it; it never invents one.

## Run

From this directory:

```powershell
python .\kernel.py --verify-canon --demo
python .\test_kernel.py
```

To emit the demo lineage append-only:

```powershell
python .\kernel.py --verify-canon --demo --emit-dir .\generated
```

## Formal layer

- `proof/OaSIs_Hierarchical_Seal_v178.lean`
- `proof/OaSIs_Hierarchical_Seal_v178.md`

The Lean file formalizes the finite hierarchy and leaves the label/orbit bijection parametric.

## Semantic scope

This is a user-defined symbolic/isomorphic software model. The gravity, plank, element, photon, black-hole, and related terms retained by the project are model-local unless independently validated as external physical claims.
