# PAL-ZIP v40 — ROTATION QUARANTINE PROVENANCE — FROZEN

**Parent:** PAL-ZIP v39  
**State:** FROZEN / 0e  
**Scope:** append-only provenance for certified policy-rotation conflicts.

## Target

v39 detects two conflicting, individually certified policy rotations from the same
pre-rotation head.

v40 freezes the consequence without rewriting either branch.

## Frozen rule

```text
CONFLICTING ROTATION VOTES
+
CERT_A
+
CERT_B
::
PRESERVE EXACTLY
```

Then append:

```text
ROTATION-QUARANTINE
::
pre_rotation_head
+
parent_policy
+
quarantined voter set
+
exact contradictory vote references
```

## Evidence rule

```text
quarantine
!=
delete vote

quarantine
!=
rewrite certificate

quarantine
!=
erase branch
```

The contradictory votes and both certified branch objects remain byte-for-byte evidence.

## Certification

- conflicting 2-of-3 quorum scenarios: 9
- quarantine events built: 9
- evidence-preservation tests: 9
- evidence mutations: 0
- exact quarantine sets: 9
- quarantine-set errors: 0
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
CERTIFIED POLICY FORK
::
both branches preserved

ROTATION EQUIVOCATION
::
authority consequence appended

PROVENANCE
::
contains both
```

So the canonical history becomes:

```text
PRE-HEAD
├─ certified child A branch
├─ certified child B branch
└─ ROTATION-QUARANTINE evidence consequence
```

No winner is selected by v40.

**STATUS: FROZEN / 0e / APPEND-ONLY DESCENDANTS**
