# PAL-ZIP v74 — RECOVERY-RANK PREFIX MERGE2 AUTHORIZATION — FROZEN

**Parent:** PAL-ZIP v73  
**State:** FROZEN / 0e  
**Scope:** require fresh authority from both exact v73 recovery-prefix parents before structural convergence becomes authorized.

## Target

v73 defines:

```text
RECOVERY-RANK-PREFIX-MERGE2(A,B)
```

as a structurally valid two-parent convergence object.

v74 freezes:

```text
STRUCTURALLY VALID RECOVERY-PREFIX MERGE
!=
AUTHORIZED RECOVERY-PREFIX MERGE
```

Neither exact recovery-prefix parent may unilaterally authorize the convergence.

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
RECOVERY-RANK-PREFIX-MERGE-AUTH:E0
```

Each exact parent independently certifies the same exact v73 merge object.

## Frozen parent certificate

```text
RECOVERY-RANK-PREFIX-MERGE-PARENT-CERT
::
exact parent recovery-prefix head
+
exact peer recovery-prefix head
+
exact RECOVERY-RANK-PREFIX-MERGE2(parent,peer)
+
fresh authority epoch
+
threshold
+
canonical approval set
```

## Frozen authorized convergence

```text
AUTHORIZED-RECOVERY-RANK-PREFIX-MERGE2
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
AUTHORIZED RECOVERY-PREFIX CONVERGENCE
::
exact parent A recovery-prefix
+
exact parent B recovery-prefix
+
fresh authority epoch
+
valid parent-A threshold cert
+
valid parent-B threshold cert
```

Therefore:

```text
ONE RECOVERY PREFIX BRANCH
cannot
unilaterally merge TWO RECOVERY PREFIX BRANCHES
```

## Boundary

v74 proves dual-parent authorization for the exact v73 structural merge object.

Replay after parent advance, epoch advance, or consumption remains a separate target.

**STATUS: FROZEN / 0e / APPEND-ONLY DESCENDANTS**
