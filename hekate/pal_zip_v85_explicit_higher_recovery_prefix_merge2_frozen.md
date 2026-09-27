# PAL-ZIP v85 — EXPLICIT HIGHER-RECOVERY PREFIX MERGE2 — FROZEN

**Parent:** PAL-ZIP v84  
**State:** FROZEN / 0e  
**Scope:** permit explicit structural convergence of two divergent v84 higher-recovery prefix heads.

## Target

v84 proves:

```text
same future syntax
!=
same higher-recovery provenance
```

Divergent higher-recovery histories remain distinct under identical later entries.

v85 introduces the only structural convergence object at this layer:

```text
HIGHER-RECOVERY-PREFIX-MERGE2(A,B)
```

which binds both exact v84 higher-recovery prefix heads.

## Frozen MERGE2

```text
HIGHER-RECOVERY-PREFIX-MERGE2
::
sort(parent_A, parent_B)
```

with:

```text
parent_A != parent_B
```

The resulting structural head is:

```text
MERGED-HIGHER-RECOVERY-PREFIX-HEAD
::
exact HIGHER-RECOVERY-PREFIX-MERGE2 object
```

## Frozen invariants

Canonical parent order:

```text
MERGE2(A,B)
=
MERGE2(B,A)
```

Exact-parent binding:

```text
MERGE2(A,B)
!=
MERGE2(A',B)
```

whenever `A' != A`.

Deep-parent ancestry therefore cannot be replaced with an older valid v83 ancestor without changing the merge identity.

The merged head is distinct from either parent:

```text
MERGED != A
MERGED != B
```

## Explicit convergence only

Matching future entries remain non-convergent:

```text
A -- same future entry --> A'
B -- same future entry --> B'
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

- parent pairs: 3
- same-rank control pairs: 3
- same-rank control failures: 0
- parent-order tests: 6
- parent-order failures: 0
- duplicate-parent attacks: 3
- duplicate-parent false accepts: 0
- merged-head/parent collisions: 0
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
HIGHER-RECOVERY PREFIX A ---------------\
                                         \
                                          MERGE2(A,B)
                                         /
HIGHER-RECOVERY PREFIX B ---------------/
```

The merged head is a new structural identity containing both exact v84 parent heads.

## Boundary

v85 defines structural convergence only.

```text
STRUCTURALLY VALID HIGHER-RECOVERY PREFIX MERGE
!=
AUTHORIZED HIGHER-RECOVERY PREFIX MERGE
```

Authorization remains a separate layer.

**STATUS: FROZEN / 0e / APPEND-ONLY DESCENDANTS**
