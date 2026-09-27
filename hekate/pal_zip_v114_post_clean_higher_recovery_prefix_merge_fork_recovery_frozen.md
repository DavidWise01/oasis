# PAL-ZIP v114 — POST-CLEAN-HIGHER-RECOVERY PREFIX-MERGE-FORK RECOVERY — FROZEN

**Parent:** PAL-ZIP v113  
**State:** FROZEN / 0e  
**Scope:** fresh recovery after append-only clean higher-recovery prefix-merge quarantine.

## Target

v113 preserves both conflicting clean higher-recovery prefix-merge histories and appends:

```text
CLEAN-HIGHER-RECOVERY-PREFIX-MERGE-QUARANTINE
```

v114 requires all recovery authority to begin from the exact v113 quarantine head.

No pre-quarantine v110/v111/v112 vote or certificate may carry forward.

## Frozen recovery epoch

```text
CLEAN-HIGHER-RECOVERY-PREFIX-MERGE-RECOVERY-EPOCH
::
exact v113 quarantine head
```

Therefore:

```text
recovery_epoch
=
F(quarantine_head)
```

Changing the quarantine head changes the recovery epoch.

## Frozen clean authority

```text
eligible
::
members - quarantined identities
```

The original threshold remains:

```text
2 / 3
```

No threshold weakening is permitted.

Fresh post-quarantine certificates bind:

```text
exact clean higher-recovery prefix parent
+
exact clean higher-recovery prefix peer
+
exact MERGE2(parent,peer)
+
exact recovery epoch
+
exact quarantine set
+
canonical clean approvals
```

## Exhaustive current geometry

Nine v112/v113 fork scenarios exist.

If the shared-parent quorum intersection is one identity:

```text
3 - 1 = 2 clean identities
```

recovery remains possible at the original threshold.

If the intersection is two identities:

```text
3 - 2 = 1 clean identity
```

recovery cannot satisfy `2 / 3` and remains safely halted.

## Certification

- fork scenarios: 9
- expected recoverable scenarios: 6
- actual recoverable scenarios: 6
- expected safe-halt scenarios: 3
- actual safe-halt scenarios: 3
- fresh target authorizations: 12
- fresh target failures: 0
- old vote replay attacks: 12
- old vote replay false accepts: 0
- old certificate replay attacks: 12
- old certificate replay false accepts: 0
- quarantined-identity attacks: 12
- quarantined-identity false accepts: 0
- wrong recovery-epoch attacks: 12
- wrong recovery-epoch false accepts: 0
- wrong-peer attacks: 12
- wrong-peer false accepts: 0
- wrong-merge attacks: 12
- wrong-merge false accepts: 0
- certificate-order tests: 48
- certificate-order failures: 0
- caller parent-order tests: 12
- caller parent-order failures: 0
- quarantine-head binding tests: 9
- quarantine-head binding failures: 0
- quarantine-set binding tests: 9
- quarantine-set binding failures: 0
- threshold-preservation checks: 9
- threshold-preservation failures: 0

**RESULT: 0e / PASS**

## Frozen invariant

```text
OLD CLEAN HIGHER-RECOVERY PREFIX-MERGE AUTHORITY
!=
FRESH POST-QUARANTINE RECOVERY AUTHORITY
```

and:

```text
QUARANTINED IDENTITY
::
cannot carry forward
```

and:

```text
POST-FORK RECOVERY
::
exact v113 quarantine-derived epoch
+
exact quarantine set
+
fresh clean votes
+
fresh clean certificates on both exact prefix parents
+
original threshold
```

If too few clean identities remain, v114 does not weaken the threshold.

It remains safely halted.

**STATUS: FROZEN / 0e / APPEND-ONLY DESCENDANTS**
