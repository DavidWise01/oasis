# PAL-ZIP v80 — RECURSIVE RECOVERY-RANK PREFIX-MERGE QUARANTINE TERMINATION — FROZEN

**Parent:** PAL-ZIP v79  
**State:** FROZEN / 0e  
**Scope:** prove repeated clean recovery-prefix merge forks cannot loop forever.

## Target

v79 shows that fresh post-quarantine recovery can itself produce a second conflicting recovery-prefix merge fork.

v80 freezes the termination measure for that higher recovery lineage.

## Frozen rank

```text
RECOVERY-RANK-PREFIX-MERGE-RECOVERY-RANK
::
|ELIGIBLE CLEAN AUTHORITY|
```

Every permitted equivocation quarantine must satisfy:

```text
Q != EMPTY
Q subset_of ELIGIBLE

ELIGIBLE'
=
ELIGIBLE - Q
```

therefore:

```text
RANK' < RANK
```

## Frozen threshold

The original authority threshold remains:

```text
2 / 3
```

for the frozen membership:

```text
T0 T1 T2
```

No recovery round may weaken that threshold.

## Frozen transition

```text
RECOVERY-RANK-PREFIX-MERGE-RECOVERY-QUARANTINE
::
prior_head
+
eligible_before
+
rank_before
+
quarantined_set
+
eligible_after
+
rank_after
+
status
```

Status is recomputed:

```text
ACTIVE
iff
rank_after >= 2

HALTED
iff
rank_after < 2
```

## Exhaustive current geometry

All admissible conflicting-quorum intersections were recursively enumerated.

- terminal paths: 6
- transitions checked: 9
- maximum quarantine rounds: 2

Every path terminates in `HALTED`.

## Certification

- transition validation failures: 0
- nondecreasing-rank transitions: 0
- terminal halt failures: 0
- identity-reentry checks: 18
- identity-reentry failures: 0
- empty-quarantine attacks: 2
- empty-quarantine false accepts: 0
- outsider-quarantine attacks: 2
- outsider-quarantine false accepts: 0
- terminal-extension checks: 6
- terminal-extension failures: 0
- prior-head binding tests: 9
- prior-head binding collisions: 0
- cycle checks: 6
- cycles found: 0
- threshold-preservation checks: 9
- threshold-preservation failures: 0

**RESULT: 0e / PASS**

## Frozen termination geometry

```text
rank 3
├─ quarantine 2
│      ↓
│   rank 1
│      ↓
│    HALTED
│
└─ quarantine 1
       ↓
    rank 2
       ↓
   quarantine 2
       ↓
    rank 0
       ↓
     HALTED
```

Therefore the current frozen higher recovery lineage terminates in at most:

```text
2 quarantine rounds
```

## Frozen invariant

```text
RECOVERY-RANK PREFIX-MERGE EQUIVOCATION QUARANTINE
::
STRICTLY DECREASES
USABLE CLEAN AUTHORITY
```

so:

```text
ACTIVE
-> lower-rank ACTIVE
-> ...
-> HALTED
```

cannot form a cycle.

No quarantined identity may re-enter the same lineage.

Termination does not select a winning recovery-prefix merge branch.

It proves only that repeated fork/recovery handling cannot continue forever without strictly consuming eligible authority.

**STATUS: FROZEN / 0e / APPEND-ONLY DESCENDANTS**
