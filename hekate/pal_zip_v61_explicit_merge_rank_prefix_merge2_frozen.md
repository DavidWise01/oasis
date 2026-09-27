# PAL-ZIP v61 — EXPLICIT MERGE-RANK PREFIX MERGE2 — FROZEN

**Parent:** PAL-ZIP v60  
**State:** FROZEN / 0e  
**Scope:** allow explicit structural convergence of two divergent merge-rank prefix heads.

## Target

v60 proves:

```text
same future syntax
!=
same merge-authority provenance
```

Therefore divergent prefixes cannot silently converge.

v61 introduces the structural convergence object:

```text
MERGE-RANK-PREFIX-MERGE2(A,B)
```

which binds both exact divergent prefix heads.

## Frozen MERGE2

```text
MERGE-RANK-PREFIX-MERGE2
::
sort(parent_A, parent_B)
```

with:

```text
parent_A != parent_B
```

The resulting structural head is:

```text
MERGED-MERGE-RANK-PREFIX-HEAD
::
exact MERGE-RANK-PREFIX-MERGE2 object
```

## Frozen invariants

Parent order is canonical:

```text
MERGE2(A,B)
=
MERGE2(B,A)
```

Exact parent identity is preserved:

```text
MERGE2(A,B)
!=
MERGE2(A',B)
```

whenever:

```text
A' != A
```

A deep parent cannot be replaced by one of its valid older prefix ancestors without changing the merge identity.

The merge head is also distinct from either parent:

```text
MERGED != A
MERGED != B
```

## Explicit convergence only

Appending the same future tail to both divergent parents still does not produce the merged head.

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

Only the explicit two-parent object creates a common structural descendant.

## Certification

- divergent parent pairs: 3
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
- same-future-after-merge checks: 6
- merged/unmerged future collisions: 0

**RESULT: 0e / PASS**

## Current geometry

```text
PREFIX A -------------------\
                             \
                              MERGE2(A,B)
                             /
PREFIX B -------------------/
```

The merged head is a new identity containing both exact parent prefix heads.

## Boundary

v61 defines **structural convergence only**.

```text
STRUCTURALLY VALID PREFIX MERGE
!=
AUTHORIZED PREFIX MERGE
```

Authorization remains a separate layer.

**STATUS: FROZEN / 0e / APPEND-ONLY DESCENDANTS**
