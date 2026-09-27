# PAL-ZIP v73 — EXPLICIT RECOVERY-RANK PREFIX MERGE2 — FROZEN

**Parent:** PAL-ZIP v72  
**State:** FROZEN / 0e  
**Scope:** permit explicit structural convergence of two divergent recovery-rank prefix heads.

## Target

v72 proves:

```text
same future syntax
!=
same recovery provenance
```

Divergent recovery histories therefore remain distinct under identical later tails.

v73 introduces the only structural convergence object at this layer:

```text
RECOVERY-RANK-PREFIX-MERGE2(A,B)
```

which binds both exact v72 parent prefix heads.

## Frozen MERGE2

```text
RECOVERY-RANK-PREFIX-MERGE2
::
sort(parent_A, parent_B)
```

with:

```text
parent_A != parent_B
```

The resulting structural head is:

```text
MERGED-RECOVERY-RANK-PREFIX-HEAD
::
exact RECOVERY-RANK-PREFIX-MERGE2 object
```

## Frozen invariants

Parent order is canonical:

```text
MERGE2(A,B)
=
MERGE2(B,A)
```

Exact parent ancestry is preserved:

```text
MERGE2(A,B)
!=
MERGE2(A',B)
```

whenever `A' != A`.

Replacing a deep v72 prefix with a valid older ancestor therefore changes the merge identity.

The merged head is distinct from either parent:

```text
MERGED != A
MERGED != B
```

## Explicit convergence only

Matching later tails still cannot collapse divergent recovery histories:

```text
A -- same tail --> A'
B -- same tail --> B'
```

does not imply:

```text
A' = B'
```

and neither continuation equals:

```text
MERGE2(A,B)
```

Only the explicit two-parent object creates the structural common descendant.

## Certification

- parent pairs: 3
- same-rank control pairs: 3
- same-rank control failures: 0
- parent-order tests: 6
- parent-order failures: 0
- duplicate-parent attacks: 3
- duplicate-parent false accepts: 0
- merge-head/parent collisions: 0
- distinct-pair merge collisions: 0
- exact-parent mutation tests: 6
- mutations preserving same merge: 0
- ancestor-substitution attacks: 6
- ancestor substitutions preserving same merge: 0
- implicit-tail vs explicit-merge checks: 6
- implicit tails equal to explicit merge: 0
- merge determinism tests: 3
- determinism failures: 0
- post-merge same-tail checks: 6
- merged/unmerged continuation collisions: 0

**RESULT: 0e / PASS**

## Frozen geometry

```text
RECOVERY PREFIX A -------------------\
                                      \
                                       MERGE2(A,B)
                                      /
RECOVERY PREFIX B -------------------/
```

The merged head is a new identity containing both exact v72 recovery-prefix heads.

## Boundary

v73 defines structural convergence only.

```text
STRUCTURALLY VALID RECOVERY-PREFIX MERGE
!=
AUTHORIZED RECOVERY-PREFIX MERGE
```

Authorization remains a separate layer.

**STATUS: FROZEN / 0e / APPEND-ONLY DESCENDANTS**
