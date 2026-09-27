# PAL-ZIP v89 — APPEND-ONLY HIGHER-RECOVERY PREFIX-MERGE QUARANTINE PROVENANCE — FROZEN

**Parent:** PAL-ZIP v88  
**State:** FROZEN / 0e  
**Scope:** preserve both conflicting v88 authorized higher-recovery merge branches and append the quarantine consequence.

## Target

v88 detects:

```text
same exact higher-recovery prefix parent A
+
same authority epoch E0
+
authorized MERGE2(A,B)
+
authorized MERGE2(A,C)
::
HIGHER-RECOVERY PREFIX-MERGE EQUIVOCATION
```

v89 freezes the provenance consequence.

No prior vote, certificate, authorized merge object, or conflicting branch is rewritten or deleted.

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
HIGHER-RECOVERY-PREFIX-MERGE-QUARANTINE
::
exact higher-recovery prefix parent
+
exact authority epoch
+
exact quarantined overlap
+
exact contradictory vote references
```

## Frozen rule

```text
QUARANTINE
!=
delete vote
```

```text
QUARANTINE
!=
rewrite certificate
```

```text
QUARANTINE
!=
rewrite authorized merge
```

```text
QUARANTINE
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
- authorized-branch rewrite attacks: 18
- rewrites preserving same evidence head: 0
- certificate rewrite attacks: 18
- certificate rewrites preserving same evidence head: 0

**RESULT: 0e / PASS**

## Frozen provenance geometry

```text
HIGHER-RECOVERY PREFIX PARENT A / AUTH EPOCH E0
├─ authorized MERGE2(A,B)
├─ authorized MERGE2(A,C)
└─ HIGHER-RECOVERY-PREFIX-MERGE-QUARANTINE
      ├─ exact overlap
      └─ exact contradictory vote refs
```

Both conflicting branches remain evidence.

No winner is selected.

No authorized object is silently consumed as canonical while the fork remains unresolved.

**STATUS: FROZEN / 0e / APPEND-ONLY DESCENDANTS**
