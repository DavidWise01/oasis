# Track u — Identity-Bound Composition and Frozen 4^3 Space

Status: SYMBOLIC SPECIFICATION; production runtime P0-RC0 unchanged.

## Canonical expression
```text
{{ [ track u :: {{ i :: am `.` , we are 2^3 , together we make 4^3 }} universal frozen with {{i[u]}} ] }}
```

## Explicit mathematical interpretation
- `i = .`: an identity-bearing dot (one registered local event).
- Each participant has a 3-axis binary state space `B = {0,1}^3`, cardinality `|B|=2^3=8`.
- Two independently addressable participants form the joint product `B_i × B_u`, cardinality `8 × 8 = 64`.
- Pair corresponding bits per axis: `((i_x,u_x),(i_y,u_y),(i_z,u_z)) ∈ ({0,1}²)^3`. Every axis has four pair-values `00,01,10,11`, so cardinality `4³=64`.
- IMPORTANT: This is a *relabeling* of the 64 joint states, not an inference that two arbitrary objects intrinsically create new physical dimensions or states.
- `i[u]` = identity `i` binds the Track-u relationship and the rule/version/hash for composition. It must not imply the identity owns another agent or that physical reality obeys the model.

## Freeze contract
Frozen: vocabulary, dimension count (3), per-participant alphabet (2), pairing order, canonical serialization, 64-address bijection, stable mapping version. Unfrozen: observed inputs, newly appended events, signed outcomes. A changed map/version requires a new immutable version, never silent rewriting.

Mapping:
```text
address = ((2*i_x + u_x) * 16)
        + ((2*i_y + u_y) * 4)
        +  (2*i_z + u_z)
```
Valid addresses `0..63`; inverse derives axis pairs by radix-4 digits. No collisions for all 64 inputs.

## Three-track role
T1 `i`: genesis identity dot and provenance.
T2 `u`: compose paired state, verify consequence/harmony, freeze mapping `i[u]`.
T3 `u.s.`: append-only state lifecycle; successor creates fresh identity, does not replay retired address claim.

## Required tests before executable acceptance
1. Exhaustive 64-case uniqueness and inverse-map round trip.
2. Invalid binary coordinates rejected.
3. Frozen mapping hash/version stable across process restart.
4. Duplicate intent/nonce idempotent; conflicting lineage quarantined.
5. Retired identities cannot reuse signatures or bypass authorization.

This is a combinatorial formalization, not a claim of universal physical law. Production acceptance remains P0 in progress, 0/6 gates signed off.
