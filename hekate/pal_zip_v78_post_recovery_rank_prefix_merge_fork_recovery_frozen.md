# PAL-ZIP v78 — POST-RECOVERY-RANK PREFIX-MERGE-FORK CLEAN RECOVERY — FROZEN

**Parent:** PAL-ZIP v77  
**State:** FROZEN / 0e  
**Scope:** fresh clean recovery after append-only recovery-rank prefix-merge quarantine.

## Target

v77 preserves both conflicting authorized recovery-prefix merge histories and appends:

```text
RECOVERY-RANK-PREFIX-MERGE-QUARANTINE
```

v78 requires all recovery authority to begin from the exact v77 quarantine head.

No pre-quarantine v74/v75 vote or certificate may carry forward.

## Frozen recovery epoch

```text
RECOVERY-RANK-PREFIX-MERGE-RECOVERY-EPOCH
::
exact v77 quarantine head
```

Therefore:

```text
recovery_epoch
=
F(quarantine_head)
```

and changing the quarantine head changes the recovery epoch.

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

Fresh clean certificates bind:

```text
exact recovery-prefix parent
+
exact recovery-prefix peer
+
exact RECOVERY-RANK-PREFIX-MERGE2 object
+
exact recovery epoch
+
exact quarantine set
+
canonical clean approvals
```

## Exhaustive current geometry

Nine v76/v77 fork scenarios exist.

If the shared-parent quorum intersection is one identity:

```text
3 - 1 = 2 clean identities
```

so recovery remains possible at the original threshold.

If the intersection is two identities:

```text
3 - 2 = 1 clean identity
```

so recovery cannot satisfy `2 / 3` and remains safely halted.

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
- threshold-preservation checks: 9
- threshold-preservation failures: 0

**RESULT: 0e / PASS**

## Frozen invariant

```text
OLD RECOVERY-PREFIX MERGE AUTHORITY
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
exact v77 quarantine-derived epoch
+
fresh clean votes
+
fresh clean certificates on both exact recovery-prefix parents
+
original threshold
```

If too few clean identities remain, v78 does not weaken the threshold.

It remains safely halted.

**STATUS: FROZEN / 0e / APPEND-ONLY DESCENDANTS**
