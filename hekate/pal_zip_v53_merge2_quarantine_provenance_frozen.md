# PAL-ZIP v53 — APPEND-ONLY MERGE2 QUARANTINE PROVENANCE — FROZEN

**Parent:** PAL-ZIP v52  
**State:** FROZEN / 0e  
**Scope:** preserve both conflicting merge branches and append the shared-parent authority consequence.

## Target

v52 detects:

```text
same parent A
+
same epoch E0
+
authorized MERGE2(A,B)
+
authorized MERGE2(A,C)
::
MERGE EQUIVOCATION
```

v53 freezes the provenance consequence.

Nothing from either conflicting merge branch is rewritten or deleted.

## Frozen evidence

Preserve exactly:

```text
all contradictory parent-A votes
+
CERT(A,B)
+
CERT(A,C)
+
authorized AB merge branch
+
authorized AC merge branch
```

Then append:

```text
MERGE-QUARANTINE
::
parent
+
epoch
+
quarantined voter set
+
exact contradictory vote references
```

## Frozen rule

```text
MERGE QUARANTINE
!=
delete vote

MERGE QUARANTINE
!=
rewrite certificate

MERGE QUARANTINE
!=
erase merge branch
```

The quarantine is an **authority consequence**, not history mutation.

## Certification

- conflicting quorum-pair scenarios: 9
- quarantine events built: 9
- evidence-preservation tests: 9
- evidence mutations: 0
- exact quarantine sets: 9
- quarantine-set errors: 0
- branch/certificate evidence-presence tests: 9
- branch/certificate evidence-presence failures: 0
- context mutation tests: 18
- context mutations preserving same event: 0
- evidence-ref mutation tests: 12
- evidence-ref mutations preserving same event: 0
- quarantine-set mutation tests: 12
- quarantine-set mutations preserving same event: 0
- append-prefix tests: 9
- append-prefix failures: 0

**RESULT: 0e / PASS**

## Frozen invariant

```text
CERTIFIED MERGE FORK
::
both merge branches preserved

MERGE EQUIVOCATION
::
quarantine consequence appended

PROVENANCE
::
contains both
```

So canonical history is:

```text
PARENT A / EPOCH E0
├─ authorized MERGE2(A,B)
├─ authorized MERGE2(A,C)
└─ MERGE-QUARANTINE(exact shared-parent overlap)
```

No winner is selected by v53.

**STATUS: FROZEN / 0e / APPEND-ONLY DESCENDANTS**
