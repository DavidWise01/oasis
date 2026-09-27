# PAL-ZIP v62 — MERGE-RANK PREFIX MERGE2 AUTHORIZATION — FROZEN

**Parent:** PAL-ZIP v61  
**State:** FROZEN / 0e  
**Scope:** require fresh authority from both exact v61 prefix parents before structural convergence becomes authorized.

## Target

v61 defines:

```text
MERGE-RANK-PREFIX-MERGE2(A,B)
```

as a structurally valid two-parent convergence object.

v62 freezes:

```text
STRUCTURALLY VALID PREFIX MERGE
!=
AUTHORIZED PREFIX MERGE
```

Neither parent may unilaterally create the authorized convergence state.

## Frozen authority context

The frozen harness uses:

```text
members
::
T0 T1 T2

threshold
::
2 / 3

authority epoch
::
PREFIX-MERGE-AUTH:E0
```

Each parent must independently certify the same exact merge object.

## Frozen parent certificate

```text
PREFIX-MERGE-PARENT-CERT
::
exact parent prefix
+
exact peer prefix
+
exact MERGE2(parent,peer)
+
fresh authority epoch
+
threshold
+
canonical approval set
```

## Frozen authorized merge

```text
AUTHORIZED-MERGE-RANK-PREFIX-MERGE2
::
fresh authority epoch
+
exact MERGE2(A,B)
+
CERT(A)
+
CERT(B)
```

Both parent certificates are mandatory.

## Exhaustive certification

- parent pairs: 3
- approval-subset pair cases: 192
- expected authorized cases: 48
- actual authorized cases: 48
- authorization mismatches: 0
- unilateral attempts: 6
- unilateral false accepts: 0
- wrong-parent certificate attacks: 3
- wrong-parent false accepts: 0
- wrong-peer certificate attacks: 3
- wrong-peer false accepts: 0
- wrong-merge certificate attacks: 3
- wrong-merge false accepts: 0
- wrong-epoch attacks: 3
- wrong-epoch false accepts: 0
- duplicate-vote attacks: 3
- duplicate-vote false accepts: 0
- outsider-vote attacks: 3
- outsider-vote false accepts: 0
- certificate-order tests: 12
- certificate-order failures: 0
- caller parent-order tests: 3
- caller parent-order failures: 0
- exact-parent mutation attacks: 3
- exact-parent mutation false accepts: 0
- authorized-object / parent collisions: 0

**RESULT: 0e / PASS**

## Frozen invariant

```text
AUTHORIZED PREFIX CONVERGENCE
::
exact parent A prefix
+
exact parent B prefix
+
fresh authority epoch
+
valid parent-A threshold cert
+
valid parent-B threshold cert
```

Therefore:

```text
ONE PREFIX BRANCH
cannot
unilaterally merge TWO PREFIX BRANCHES
```

and:

```text
old authority context
!=
fresh authority context
```

## Boundary

v62 proves dual-parent authorization for the exact v61 prefix merge object.

Replay after either parent advances or after the authorized merge head is consumed remains a separate target.

**STATUS: FROZEN / 0e / APPEND-ONLY DESCENDANTS**
