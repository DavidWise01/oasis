# PAL-ZIP v113 — APPEND-ONLY CLEAN HIGHER-RECOVERY PREFIX-MERGE QUARANTINE PROVENANCE — FROZEN

**Parent:** PAL-ZIP v112  
**State:** FROZEN / 0e  
**Scope:** preserve every conflicting v112 vote, certificate, authorized merge, and branch head, then append the quarantine consequence without rewriting history.

## Target

v112 detects:

```text
same exact clean higher-recovery prefix parent A
+
same authority epoch E0
+
authorized MERGE2(A,B)
+
authorized MERGE2(A,C)
::
CLEAN HIGHER-RECOVERY PREFIX MERGE EQUIVOCATION
```

v113 freezes append-only provenance.

No prior vote, certificate, authorized merge object, or conflicting branch may be rewritten or deleted.

## Preserved evidence

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
CLEAN-HIGHER-RECOVERY-PREFIX-MERGE-QUARANTINE
::
exact clean prefix parent
+
exact authority epoch
+
exact quarantined overlap
+
exact contradictory vote references
```

## Frozen rule

```text
QUARANTINE != delete vote
QUARANTINE != rewrite certificate
QUARANTINE != rewrite authorized merge
QUARANTINE != erase conflicting branch
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
- vote rewrite attacks: 36
- vote rewrites preserving same evidence head: 0

**RESULT: 0e / PASS**

## Frozen provenance geometry

```text
CLEAN HIGHER-RECOVERY PREFIX PARENT A / AUTH EPOCH E0
├─ authorized MERGE2(A,B)
├─ authorized MERGE2(A,C)
└─ CLEAN-HIGHER-RECOVERY-PREFIX-MERGE-QUARANTINE
      ├─ exact overlap
      └─ exact contradictory vote refs
```

Both conflicting branches remain evidence.

No winner is selected.

No authorized object is silently consumed as canonical while the fork remains unresolved.

**STATUS: FROZEN / 0e / APPEND-ONLY DESCENDANTS**
