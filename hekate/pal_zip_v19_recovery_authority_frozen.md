# PAL-ZIP v19 — UNANIMOUS SURVIVOR RECOVERY AUTHORITY — FROZEN

**Parent:** PAL-ZIP v18  
**State:** FROZEN / 0e  
**Scope:** formal authorization of successor configuration after quarantine.

## Target

v18 defines a safe successor committee geometry but intentionally leaves
the approval rule separate.

v19 freezes a conservative recovery authority rule:

```text
RECOVERY APPROVAL
::
ALL surviving non-quarantined identities
from the old committee
```

For the current test geometry:

```text
old committee
::
G0 G1 G2 G3

quarantined
::
G1 G2

survivors
::
G0 G3

recovery threshold
::
2 / 2 survivors
```

## Certification

- surviving identities: 2
- survivor approval subsets tested: 4
- expected accepted subsets: 1
- actual accepted subsets: 1
- subset mismatches: 0
- duplicate-vote attacks: 2
- duplicate false accepts: 0
- quarantined substitution attacks: 2
- quarantined false accepts: 0
- newcomer substitution attacks: 2
- newcomer false accepts: 0
- wrong-recovery attacks: 2
- wrong-recovery false accepts: 0
- vote-order tests: 2
- order failures: 0

**RESULT: 0e / PASS**

## Frozen certificate

```text
RCERT
::
exact RECOVER object
+
canonical unanimous survivor approvals
```

## Frozen invariant

```text
SURVIVOR
::
old committee
-
quarantined set
```

and:

```text
ACCEPT RECOVERY
iff
every survivor approves
the exact same RECOVER object
```

This is intentionally a recovery rule, not a general replacement for the normal 3-of-4 merge quorum.

**STATUS: FROZEN / 0e / APPEND-ONLY DESCENDANTS**
