# PAL-ZIP v42 — CLEAN-RECOVERY FORK PROTECTION — FROZEN

**Parent:** PAL-ZIP v41  
**State:** FROZEN / 0e  
**Scope:** prevent clean recovery from becoming a back door around rotation-fork safety.

## Target

v41 allows a fresh rotation after quarantine only when enough clean parent-policy voters remain.

v42 attacks that recovery path itself:

```text
same quarantine head
+
same clean voters
+
approve child A
+
approve child B
```

Both clean branches may individually satisfy the original parent threshold.

That must create another explicit fork/equivocation rather than silently choosing a child.

## Frozen clean-recovery equivocation

```text
same voter
+
same quarantine_head
+
same parent
+
approve child A
+
approve child B
+
A != B
::
CLEAN-RECOVERY EQUIVOCATION
```

## Frozen geometry

For every v41-recoverable `P2 = 2/3` scenario:

```text
first quarantine intersection = 1
↓
exactly 2 clean voters remain
```

If both clean voters approve both children:

```text
child A cert :: valid 2/3
child B cert :: valid 2/3
```

but both clean voters have equivocated.

Second quarantine therefore yields:

```text
remaining clean authority
::
EMPTY
```

and neither child remains authorized.

## Certification

- v41-recoverable scenarios: 6
- scenarios with two valid clean certificates: 6
- branch-head collisions: 0
- same-tail tests: 6
- silent rejoins: 0
- exact clean-equivocator sets: 6
- equivocation-set errors: 0
- aggregate remaining clean authority after second quarantine: 0
- child A branches surviving second quarantine: 0
- child B branches surviving second quarantine: 0
- certificate voter-order tests: 12
- certificate order failures: 0
- different-head controls: 3
- different-head false equivocation: 0
- first-quarantined voter reuse attacks: 6
- first-quarantined voter false accepts: 0

**RESULT: 0e / PASS**

## Frozen consequence

```text
CLEAN RECOVERY
cannot bypass
CERTIFIED FORK SAFETY
```

and:

```text
two conflicting clean 2/3 certificates
from same quarantine head
::
second equivocation quarantine
::
clean authority = EMPTY
::
SAFE HALT
```

No winner is selected. Both clean branch histories remain evidence.

**STATUS: FROZEN / 0e / APPEND-ONLY DESCENDANTS**
