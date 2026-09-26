# PAL-ZIP v49 — PREFIX-AWARE EXPLICIT MERGE2 — FROZEN

**Parent:** PAL-ZIP v48  
**State:** FROZEN / 0e  
**Scope:** explicit convergence of two divergent prefix histories.

## Target

v48 proves:

```text
same future
!=
same provenance
```

So two divergent prefix heads cannot silently converge.

v49 introduces the only structural convergence primitive in this lineage:

```text
MERGE2
```

The merge must bind **both exact parent heads**.

## Frozen MERGE2

```text
PREFIX-MERGE2
::
sort(parent_A, parent_B)
```

with:

```text
parent_A != parent_B
```

The merged prefix identity is:

```text
MERGED-PREFIX-HEAD
::
exact PREFIX-MERGE2 object
```

## Frozen invariants

Parent order is canonical:

```text
MERGE2(A,B)
=
MERGE2(B,A)
```

but parent identity is exact:

```text
MERGE2(A,B)
!=
MERGE2(A',B)
```

when:

```text
A' != A
```

Likewise, replacing a deep parent with one of its valid older ancestors changes the merge identity.

A merge head must also be distinct from either parent:

```text
MERGED != A
MERGED != B
```

## Explicit convergence only

```text
A != B
```

does not become equal because of common later tails.

Only:

```text
MERGE2(A,B)
```

creates a new common descendant identity.

So:

```text
implicit convergence
::
forbidden

explicit two-parent convergence
::
represented
```

## Certification

- seed parent pairs: 3
- deep parent pairs: 3
- parent-order tests: 12
- parent-order failures: 0
- duplicate-parent attacks: 6
- duplicate-parent false accepts: 0
- merge-head/parent collisions: 0
- distinct-pair merge collisions: 0
- parent-mutation tests: 12
- parent mutations preserving same merge: 0
- ancestor-substitution attacks: 6
- ancestor substitutions preserving same merge: 0
- implicit-vs-explicit checks: 6
- implicit heads equal to explicit merge: 0
- merge determinism tests: 6
- merge determinism failures: 0

**RESULT: 0e / PASS**

## Current geometry

```text
A -------------------\
                      \
                       MERGE2(A,B)
                      /
B -------------------/
```

The new merge head preserves both exact parent identities inside the merged object.

## Boundary

v49 defines **structural merge identity only**.

It does not yet define who is allowed to authorize a merge.

```text
STRUCTURALLY VALID MERGE
!=
AUTHORIZED MERGE
```

That authority layer remains separate.

**STATUS: FROZEN / 0e / APPEND-ONLY DESCENDANTS**
