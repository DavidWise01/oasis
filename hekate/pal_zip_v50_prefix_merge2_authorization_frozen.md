# PAL-ZIP v50 — PREFIX-AWARE MERGE2 AUTHORIZATION — FROZEN

**Parent:** PAL-ZIP v49  
**State:** FROZEN / 0e  
**Scope:** require independent authority from both exact prefix parents before explicit convergence.

## Target

v49 defines the structural object:

```text
PREFIX-MERGE2(A,B)
```

v50 freezes the authority rule:

```text
STRUCTURALLY VALID MERGE
!=
AUTHORIZED MERGE
```

Neither parent may unilaterally manufacture convergence.

## Frozen parent certificate

For the frozen test geometry, each parent uses:

```text
members
::
T0 T1 T2

threshold
::
2 / 3
```

Each parent signs the **same exact MERGE2 object**, but under its own exact parent head:

```text
PARENT-MERGE-CERT
::
parent_head
+
exact PREFIX-MERGE2
+
threshold
+
canonical approval set
```

## Frozen authorization

```text
AUTHORIZED-PREFIX-MERGE2
::
exact MERGE2(A,B)
+
CERT(A)
+
CERT(B)
```

Both certificates are mandatory.

So:

```text
CERT(A) only
::
REJECT

CERT(B) only
::
REJECT
```

and:

```text
CERT(A for another merge)
::
REJECT
```

## Parent symmetry

The structural merge is parent-order canonical:

```text
MERGE2(A,B)
=
MERGE2(B,A)
```

and the authorization object is also canonical when the corresponding certificates move with
their exact parent identities.

## Exhaustive certification

- parent pairs exercised: 6
- approval-subset pair cases: 384
- expected authorized cases: 96
- actual authorized cases: 96
- authorization mismatches: 0
- unilateral attempts: 12
- unilateral false accepts: 0
- wrong-parent certificate attacks: 6
- wrong-parent false accepts: 0
- wrong-merge certificate attacks: 6
- wrong-merge false accepts: 0
- duplicate-vote attacks: 6
- duplicate-vote false accepts: 0
- outsider-vote attacks: 6
- outsider-vote false accepts: 0
- certificate order tests: 24
- certificate order failures: 0
- caller parent-order tests: 6
- caller parent-order failures: 0
- exact-parent mutation attacks: 6
- parent-mutation false accepts: 0
- ancestor-substitution attacks: 3
- ancestor-substitution false accepts: 0
- authorized merge / parent collisions: 0

**RESULT: 0e / PASS**

## Frozen invariant

```text
EXPLICIT CONVERGENCE
::
two exact parent heads
+
two parent-bound certificates
```

Therefore:

```text
ONE BRANCH
cannot
unilaterally merge TWO BRANCHES
```

and:

```text
ancestor authority
!=
descendant authority
```

when the exact parent head has changed.

## Boundary

v50 proves dual-parent authorization under the frozen `2 / 3` parent-certificate policy used by
this test harness.

It does not yet define what happens if the two parent certificates themselves conflict,
equivocate, or are replayed at a later merged head.

**STATUS: FROZEN / 0e / APPEND-ONLY DESCENDANTS**
