# PAL-ZIP v55 — CLEAN-MERGE RECOVERY FORK PROTECTION — FROZEN

**Parent:** PAL-ZIP v54  
**State:** FROZEN / 0e  
**Scope:** prevent clean merge recovery from recreating the merge fork it was designed to recover from.

## Target

v54 allows a fresh merge attempt only from a quarantine-derived recovery epoch using
non-quarantined identities.

v55 attacks that recovery path itself:

```text
same recovery epoch
+
same clean parent A authority
+
freshly authorize MERGE2(A,B)
+
freshly authorize MERGE2(A,C)
```

Both recovery branches can individually satisfy the original `2 / 3` threshold.

That must create a second merge fork/equivocation, not two canonical convergence paths.

## Frozen clean-merge equivocation

```text
same voter
+
same parent
+
same recovery epoch
+
approve peer B / merge AB
+
approve peer C / merge AC
+
AB != AC
::
CLEAN-MERGE RECOVERY EQUIVOCATION
```

## Frozen recoverable geometry

Every v54-recoverable scenario has:

```text
first quarantine intersection = 1
↓
2 clean identities remain
```

Those two clean identities are exactly the full remaining `2 / 3` authority.

If both authorize both merge targets:

```text
AB clean cert :: valid
AC clean cert :: valid
```

but both clean voters have equivocated.

The second quarantine therefore yields:

```text
remaining clean authority
::
EMPTY
```

so neither recovery merge remains authorized.

## Certification

- v54-recoverable scenarios: 6
- scenarios with two fresh clean merge authorizations: 6
- recovery branch-head collisions: 0
- same-tail tests: 6
- silent rejoins: 0
- exact clean-equivocator sets: 6
- clean-equivocator set errors: 0
- aggregate remaining clean authority after second quarantine: 0
- AB branches surviving second quarantine: 0
- AC branches surviving second quarantine: 0
- clean certificate order tests: 24
- clean certificate order failures: 0
- different-recovery-epoch controls: 3
- different-epoch false equivocation: 0
- same-merge repeat controls: 3
- same-merge repeat false equivocation: 0
- different-parent controls: 3
- different-parent false equivocation: 0
- first-quarantined identity reuse attacks: 6
- first-quarantined identity false accepts: 0

**RESULT: 0e / PASS**

## Frozen consequence

```text
CLEAN MERGE RECOVERY
cannot bypass
MERGE FORK SAFETY
```

and:

```text
two conflicting fresh 2/3 merge authorizations
from same recovery epoch
::
second merge equivocation quarantine
::
clean authority = EMPTY
::
SAFE HALT
```

Both clean recovery branch histories remain evidence.

No winner is selected.

**STATUS: FROZEN / 0e / APPEND-ONLY DESCENDANTS**
