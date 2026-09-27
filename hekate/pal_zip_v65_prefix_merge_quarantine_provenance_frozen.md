# PAL-ZIP v65 — APPEND-ONLY PREFIX-MERGE QUARANTINE PROVENANCE — FROZEN

**Parent:** PAL-ZIP v64  
**State:** FROZEN / 0e  
**Scope:** preserve both conflicting authorized prefix-merge branches and append the quarantine consequence.

## Target

v64 detects:

```text
same exact parent prefix A
+
same authority epoch E0
+
authorized MERGE2(A,B)
+
authorized MERGE2(A,C)
::
PREFIX-MERGE EQUIVOCATION
```

v65 freezes the append-only provenance consequence.

Nothing from either conflicting authorization branch is rewritten or deleted.

## Frozen preserved evidence

Preserve exactly:

```text
all contradictory shared-parent A votes
+
peer-side votes
+
CERT(A,B)
+
CERT(A,C)
+
CERT(B,A)
+
CERT(C,A)
+
authorized AB object
+
authorized AC object
+
AB branch head
+
AC branch head
```

Then append:

```text
PREFIX-MERGE-QUARANTINE
::
exact parent prefix
+
exact authority epoch
+
exact quarantined overlap
+
exact contradictory vote references
```

## Frozen rule

```text
PREFIX-MERGE QUARANTINE
!=
delete vote
```

```text
PREFIX-MERGE QUARANTINE
!=
rewrite certificate
```

```text
PREFIX-MERGE QUARANTINE
!=
rewrite authorized merge
```

```text
PREFIX-MERGE QUARANTINE
!=
erase conflicting branch
```

The quarantine is an authority consequence, not a history mutation.

## Certification

- conflict scenarios: 9
- quarantine events: 9
- evidence-preservation tests: 9
- evidence mutations: 0
- branch/certificate presence tests: 9
- presence failures: 0
- exact quarantine sets: 9
- quarantine-set errors: 0
- context mutation tests: 18
- context mutations preserving same event: 0
- evidence-ref mutation tests: 24
- evidence-ref mutations preserving same event: 0
- quarantine-set mutation tests: 12
- quarantine-set mutations preserving same event: 0
- append-prefix tests: 9
- append-prefix failures: 0
- branch-rewrite attacks: 18
- rewrites preserving same evidence head: 0

**RESULT: 0e / PASS**

## Frozen provenance geometry

```text
PREFIX PARENT A / AUTH EPOCH E0
├─ authorized MERGE2(A,B)
├─ authorized MERGE2(A,C)
└─ PREFIX-MERGE-QUARANTINE
      ├─ exact overlap
      └─ exact contradictory vote refs
```

Both conflicting branches remain evidence.

No winner is selected.

No authorized object is silently consumed as canonical while the fork remains unresolved.

**STATUS: FROZEN / 0e / APPEND-ONLY DESCENDANTS**
