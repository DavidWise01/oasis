# PAL-ZIP v110 — CLEAN HIGHER-RECOVERY PREFIX MERGE2 AUTHORIZATION — FROZEN

**Parent:** PAL-ZIP v109  
**State:** FROZEN / 0e  
**Scope:** require fresh dual-parent authority before a structurally valid v109 clean higher-recovery prefix convergence becomes authorized.

## Target

```text
CLEAN-HIGHER-RECOVERY-RANK-PREFIX-MERGE2
::
sort(parent_A, parent_B)
```

```text
STRUCTURALLY VALID CLEAN HIGHER-RECOVERY PREFIX MERGE
!=
AUTHORIZED CLEAN HIGHER-RECOVERY PREFIX MERGE
```

Neither exact v109 parent can authorize the two-parent convergence alone.

## Frozen authority

```text
members :: T0 T1 T2
threshold :: 2 / 3
epoch :: CLEAN-HIGHER-RECOVERY-PREFIX-MERGE-AUTH:E0
```

## Frozen parent certificate

```text
CLEAN-HIGHER-RECOVERY-PREFIX-MERGE-PARENT-CERT
::
exact v109 parent
+
exact peer v109 parent
+
exact v109 MERGE2(parent,peer)
+
exact authority epoch
+
threshold
+
canonical approval set
```

## Frozen authorized convergence

```text
AUTHORIZED-CLEAN-HIGHER-RECOVERY-PREFIX-MERGE2
::
exact authority epoch
+
exact v109 MERGE2(A,B)
+
CERT(A)
+
CERT(B)
```

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
AUTHORIZED CLEAN HIGHER-RECOVERY PREFIX CONVERGENCE
::
exact v109 parent A
+
exact v109 parent B
+
exact v109 MERGE2(A,B)
+
exact fresh authority epoch
+
valid 2/3 parent-A cert
+
valid 2/3 parent-B cert
```

```text
ONE v109 CLEAN HIGHER-RECOVERY PREFIX
cannot
unilaterally merge TWO v109 CLEAN PREFIX HISTORIES
```

Replay after parent advance, peer substitution, epoch advance, or consumption is the next target.

**STATUS: FROZEN / 0e / APPEND-ONLY DESCENDANTS**
