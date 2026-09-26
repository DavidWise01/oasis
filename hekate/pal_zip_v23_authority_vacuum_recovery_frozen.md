# PAL-ZIP v23 — AUTHORITY-VACUUM RECOVERY — FROZEN

**Parent:** PAL-ZIP v22  
**State:** FROZEN / 0e  
**Scope:** formal recovery when effective authority is empty.

## Target

v22 can correctly halt at:

```text
effective authority
::
EMPTY
```

v23 provides a recovery path that cannot be authorized by any identity implicated
in the conflicting history and cannot let the recovery authority appoint itself.

## Frozen reserve authority

```text
RESERVE
::
R0 R1 R2 R3

THRESHOLD
::
3 / 4
```

The reserve committee is assumed to be pre-anchored before the authority vacuum.
It is separate from the implicated authority set.

## Frozen successor constraints

```text
successor ∩ implicated
::
EMPTY

successor ∩ reserve
::
EMPTY
```

Therefore:

```text
old conflicting authority
cannot appoint itself

quarantined authority
cannot re-enter

reserve authority
cannot appoint itself
```

## Frozen object

```text
VACUUM-RECOVER
::
vacuum_root
+
reserve_committee
+
implicated_set
+
successor_committee
```

and:

```text
VRCERT
::
exact VACUUM-RECOVER
+
canonical 3-of-4 reserve approval
```

## Certification

- candidate successor committees: 5
- valid recovery objects: 5
- valid-object failures: 0
- member-order tests: 120
- member-order failures: 0
- reserve approval subsets: 80
- expected reserve accepts: 25
- actual reserve accepts: 25
- reserve subset mismatches: 0
- implicated re-entry attacks: 4
- implicated re-entry false accepts: 0
- reserve self-appointment attacks: 4
- reserve self-appointment false accepts: 0
- outsider-vote attacks: 3
- outsider-vote false accepts: 0
- wrong-recovery vote attacks: 1
- wrong-recovery vote false accepts: 0
- certificate order tests: 30
- certificate order failures: 0
- vacuum-root mutations: 5
- vacuum-root mutations preserving same object: 0

**RESULT: 0e / PASS**

## Frozen invariant

```text
AUTHORITY VACUUM
::
does not permit self-repair by implicated authority
```

Recovery requires:

```text
pre-anchored reserve authority
+
exact vacuum root
+
disjoint successor committee
+
3 / 4 reserve approval
```

This restores a route to liveness without rewriting the conflict evidence.

**STATUS: FROZEN / 0e / APPEND-ONLY DESCENDANTS**
