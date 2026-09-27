# PAL-ZIP v86 — HIGHER-RECOVERY PREFIX MERGE2 AUTHORIZATION — FROZEN

**Parent:** PAL-ZIP v85  
**State:** FROZEN / 0e  
**Scope:** require fresh authority from both exact v85 higher-recovery prefix parents before structural convergence becomes authorized.

## Target

v85 defines:

```text
HIGHER-RECOVERY-PREFIX-MERGE2(A,B)
```

as a structurally valid two-parent convergence object.

v86 freezes:

```text
STRUCTURALLY VALID HIGHER-RECOVERY PREFIX MERGE
!=
AUTHORIZED HIGHER-RECOVERY PREFIX MERGE
```

Neither exact higher-recovery prefix parent may unilaterally authorize the convergence.

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
HIGHER-RECOVERY-PREFIX-MERGE-AUTH:E0
```

Each exact parent independently certifies the same exact v85 merge object.

## Frozen parent certificate

```text
HIGHER-RECOVERY-PREFIX-MERGE-PARENT-CERT
::
exact higher-recovery parent prefix
+
exact peer higher-recovery prefix
+
exact HIGHER-RECOVERY-PREFIX-MERGE2(parent,peer)
+
fresh authority epoch
+
threshold
+
canonical approval set
```

## Frozen authorized convergence

```text
AUTHORIZED-HIGHER-RECOVERY-PREFIX-MERGE2
::
fresh authority epoch
+
exact MERGE2(A,B)
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

**RESULT: 0e / PASS**

## Frozen invariant

```text
AUTHORIZED HIGHER-RECOVERY PREFIX CONVERGENCE
::
exact parent A higher-recovery prefix
+
exact parent B higher-recovery prefix
+
fresh authority epoch
+
valid parent-A threshold cert
+
valid parent-B threshold cert
```

Therefore:

```text
ONE HIGHER-RECOVERY PREFIX BRANCH
cannot
unilaterally merge TWO HIGHER-RECOVERY PREFIX BRANCHES
```

## Boundary

v86 proves dual-parent authorization for the exact v85 structural merge object.

Replay after parent advance, epoch advance, or consumption remains a separate target.

**STATUS: FROZEN / 0e / APPEND-ONLY DESCENDANTS**
