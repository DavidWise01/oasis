# PAL-ZIP v97 — EXPLICIT HIGHER-RECOVERY RANK-PREFIX MERGE2 — FROZEN

**Parent:** PAL-ZIP v96  
**State:** FROZEN / 0e  
**Scope:** explicit structural convergence of two exact divergent v96 higher-recovery rank-prefix heads.

## Target

v96 proves:

```text
DIVERGED HIGHER-RECOVERY PREFIX
+
IDENTICAL FUTURE TAILS
::
STILL DIVERGED
```

Therefore matching future syntax cannot create convergence.

v97 introduces the explicit structural convergence object:

```text
HIGHER-RECOVERY-PREFIX-MERGE-RECOVERY-RANK-PREFIX-MERGE2
::
sort(parent_A, parent_B)
```

with:

```text
parent_A != parent_B
```

Both parents are exact v96 prefix identities.

## Frozen merged head

```text
MERGED-HIGHER-RECOVERY-PREFIX-MERGE-RECOVERY-RANK-PREFIX-HEAD
::
exact HIGHER-RECOVERY-PREFIX-MERGE-RECOVERY-RANK-PREFIX-MERGE2
```

The merged head is a new structural identity.

It is not either parent.

## Canonical symmetry

```text
MERGE2(A,B)
=
MERGE2(B,A)
```

but:

```text
MERGE2(A,B)
!=
MERGE2(A,C)
```

when the exact parent pair changes.

## Exact-parent binding

Any mutation of either parent changes merge identity:

```text
A != A'
::
MERGE2(A,B)
!=
MERGE2(A',B)
```

Replacing a deep v96 parent with its genuine earlier v95 seed ancestor also changes identity.

Therefore:

```text
VALID ANCESTOR
!=
EXACT CURRENT MERGE PARENT
```

## Explicit convergence only

Identical future syntax remains insufficient:

```text
A -- same future --> A'
B -- same future --> B'
```

does not imply:

```text
A' = B'
```

and neither continuation equals the explicit v97 merge head.

The only structural convergence introduced at this layer is the exact two-parent `MERGE2` object.

## Certification

- parent pairs: 3
- same-rank control pairs: 3
- same-rank control failures: 0
- parent-order tests: 6
- parent-order failures: 0
- duplicate-parent attacks: 3
- duplicate-parent false accepts: 0
- merged-head / parent collisions: 0
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
v96 HIGHER-RECOVERY RANK-PREFIX A --------\
                                           \
                                            MERGE2(A,B)
                                           /
v96 HIGHER-RECOVERY RANK-PREFIX B --------/
```

## Boundary

v97 defines structural convergence only.

```text
STRUCTURALLY VALID HIGHER-RECOVERY RANK-PREFIX MERGE
!=
AUTHORIZED HIGHER-RECOVERY RANK-PREFIX MERGE
```

Authorization remains a separate next layer.

No winner is selected.

**STATUS: FROZEN / 0e / APPEND-ONLY DESCENDANTS**
