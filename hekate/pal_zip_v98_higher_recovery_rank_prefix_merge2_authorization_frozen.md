# PAL-ZIP v98 — HIGHER-RECOVERY RANK-PREFIX MERGE2 AUTHORIZATION — FROZEN

**Parent:** PAL-ZIP v97  
**State:** FROZEN / 0e  
**Scope:** require fresh dual-parent authority before a structurally valid v97 higher-recovery rank-prefix convergence becomes authorized.

## Target

v97 defines the structural object:

```text
HIGHER-RECOVERY-PREFIX-MERGE-RECOVERY-RANK-PREFIX-MERGE2
::
sort(parent_A, parent_B)
```

v98 freezes:

```text
STRUCTURALLY VALID HIGHER-RECOVERY RANK-PREFIX MERGE
!=
AUTHORIZED HIGHER-RECOVERY RANK-PREFIX MERGE
```

Neither exact v97 parent can authorize the two-parent convergence alone.

## Frozen authority context

```text
members
::
T0 T1 T2

threshold
::
2 / 3

authority epoch
::
HIGHER-RECOVERY-RANK-PREFIX-MERGE-AUTH:E0
```

## Frozen parent certificate

```text
HIGHER-RECOVERY-RANK-PREFIX-MERGE-PARENT-CERT
::
exact v97 parent
+
exact peer v97 parent
+
exact v97 MERGE2(parent,peer)
+
exact authority epoch
+
threshold
+
canonical approval set
```

## Frozen authorized convergence

```text
AUTHORIZED-HIGHER-RECOVERY-RANK-PREFIX-MERGE2
::
exact authority epoch
+
exact v97 MERGE2(A,B)
+
CERT(A)
+
CERT(B)
```

Both exact-parent certificates are mandatory.

## Certification

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
- authorized-pair collisions: 0

**RESULT: 0e / PASS**

## Frozen invariant

```text
AUTHORIZED HIGHER-RECOVERY RANK-PREFIX CONVERGENCE
::
exact v97 parent A
+
exact v97 parent B
+
exact v97 MERGE2(A,B)
+
exact fresh authority epoch
+
valid 2/3 parent-A cert
+
valid 2/3 parent-B cert
```

Therefore:

```text
ONE v97 HIGHER-RECOVERY RANK-PREFIX
cannot
unilaterally merge TWO v97 RANK-PREFIX HISTORIES
```

## Boundary

v98 proves dual-parent authorization for the exact v97 structural merge object.

Replay after parent advance, epoch advance, or consumption remains a separate target.

**STATUS: FROZEN / 0e / APPEND-ONLY DESCENDANTS**
