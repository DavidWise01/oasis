# PAL-ZIP v54 — POST-MERGE-FORK CLEAN RECOVERY — FROZEN

**Parent:** PAL-ZIP v53  
**State:** FROZEN / 0e  
**Scope:** fresh recovery after append-only merge quarantine.

## Target

After:

```text
CERTIFIED MERGE FORK
↓
MERGE-QUARANTINE
```

neither conflicting convergence path may reuse the old merge epoch, old certificates,
old votes, or quarantined identities.

Recovery must start from a fresh epoch derived from the quarantine head.

## Frozen recovery epoch

```text
RECOVERY-EPOCH
::
MERGE-RECOVERY-EPOCH(quarantine_head)
```

## Frozen recovery authority

```text
eligible
::
members
-
quarantined identities
```

The original threshold remains:

```text
2 / 3
```

and both exact merge parents require fresh certificates in the new recovery epoch.

```text
AUTHORIZED-CLEAN-MERGE2
::
fresh parent-A cert
+
fresh peer cert
+
exact merge id
+
exact recovery epoch
+
exact quarantine set
```

## Exhaustive 2-of-3 fork geometry

Nine v52/v53 fork scenarios exist.

When the conflicting parent quorums intersect in one identity:

```text
3 - 1 = 2 clean identities
```

so the original threshold can still be met.

When they intersect in two identities:

```text
3 - 2 = 1 clean identity
```

so recovery cannot meet `2 / 3` and remains safely halted.

## Certification

- fork scenarios: 9
- expected recoverable scenarios: 6
- actual recoverable scenarios: 6
- expected safe-halt scenarios: 3
- actual safe-halt scenarios: 3
- fresh target authorizations: 12
- fresh target failures: 0
- old-epoch vote replay attacks: 12
- old-epoch vote replay false accepts: 0
- old-certificate replay attacks: 12
- old-certificate replay false accepts: 0
- quarantined-identity attacks: 12
- quarantined-identity false accepts: 0
- wrong-peer attacks: 12
- wrong-peer false accepts: 0
- wrong-merge attacks: 12
- wrong-merge false accepts: 0
- certificate ordering tests: 48
- certificate ordering failures: 0
- caller parent-order tests: 12
- caller parent-order failures: 0

**RESULT: 0e / PASS**

## Frozen invariant

```text
OLD MERGE AUTHORITY
!=
FRESH RECOVERY AUTHORITY
```

and:

```text
QUARANTINED IDENTITY
::
cannot carry forward
```

and:

```text
RECOVERY
::
fresh quarantine-derived epoch
+
fresh clean votes
+
fresh certificates on both exact parents
+
original threshold
```

If too few clean identities remain, v54 does not weaken the threshold.

It remains safely halted.

**STATUS: FROZEN / 0e / APPEND-ONLY DESCENDANTS**
