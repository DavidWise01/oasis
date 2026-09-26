# PAL-ZIP v56 — RECURSIVE MERGE-QUARANTINE TERMINATION — FROZEN

**Parent:** PAL-ZIP v55  
**State:** FROZEN / 0e  
**Scope:** prove repeated merge-equivocation quarantine cannot loop forever.

## Target

v55 shows that clean recovery can itself fork and trigger a second quarantine.

v56 freezes the termination measure for the merge-authority lineage.

## Frozen rank

```text
MERGE-AUTH-RANK
::
|ELIGIBLE MERGE AUTHORITY|
```

Every permitted merge-equivocation quarantine must satisfy:

```text
Q != EMPTY
Q subset_of ELIGIBLE
ELIGIBLE' = ELIGIBLE - Q
```

therefore:

```text
RANK' < RANK
```

## Frozen transition

```text
MERGE-AUTH-QUARANTINE
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

Status is:

```text
ACTIVE
iff
rank_after >= threshold

HALTED
iff
rank_after < threshold
```

The frozen threshold remains:

```text
2
```

over:

```text
T0 T1 T2
```

## Exhaustive current geometry

All admissible conflicting-quorum intersection sets were enumerated recursively.

The resulting merge-quarantine lineage has:

- terminal paths: 6
- transitions checked: 9
- maximum quarantine rounds: 2

Every path ends in `HALTED`.

## Certification

- transition validation failures: 0
- nondecreasing-rank transitions: 0
- terminal halt failures: 0
- identity-reentry attacks: 18
- identity-reentry false accepts: 0
- empty-quarantine attacks: 2
- empty-quarantine false accepts: 0
- outsider-quarantine attacks: 2
- outsider-quarantine false accepts: 0
- terminal-extension attacks: 6
- terminal-extension false accepts: 0
- prior-head replay tests: 9
- prior-head replay collisions: 0
- cycle checks: 6
- cycles found: 0
- rank-bound violations: 0

**RESULT: 0e / PASS**

## Frozen invariant

```text
MERGE EQUIVOCATION QUARANTINE
::
STRICTLY DECREASES
USABLE MERGE AUTHORITY
```

Therefore:

```text
ACTIVE
-> lower-rank ACTIVE
-> ...
-> HALTED
```

cannot form a cycle.

For the current three-identity / threshold-two geometry:

```text
rank 3
├─ quarantine 2 -> rank 1 -> HALTED
└─ quarantine 1 -> rank 2 -> ACTIVE
                     |
                     └─ quarantine 2 -> rank 0 -> HALTED
```

So the current lineage terminates in at most:

```text
2 quarantine rounds
```

No quarantined identity may re-enter the same lineage.

## Boundary

Termination does not choose a winning merge branch.

It proves only:

```text
repeated merge-fork handling
cannot loop forever
without strictly consuming eligible authority
```

**STATUS: FROZEN / 0e / APPEND-ONLY DESCENDANTS**
