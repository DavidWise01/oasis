# PAL-ZIP v67 — CLEAN PREFIX-MERGE RECOVERY FORK PROTECTION — FROZEN

**Parent:** PAL-ZIP v66  
**State:** FROZEN / 0e  
**Scope:** prevent clean prefix-merge recovery from recreating the fork it is recovering from.

## Target

v66 permits fresh recovery only from the quarantine-derived recovery epoch using non-quarantined identities.

v67 attacks that clean recovery path itself:

```text
same recovery epoch
+
same clean exact parent prefix A
+
freshly authorize MERGE2(A,B)
+
freshly authorize MERGE2(A,C)
```

Both recovery branches can individually satisfy the original `2 / 3` threshold.

That must produce a second prefix-merge equivocation and safe halt, not two canonical convergence paths.

## Frozen clean recovery equivocation

```text
same clean voter
+
same exact parent prefix
+
same recovery epoch
+
approve peer B / merge AB
+
approve peer C / merge AC
+
AB != AC
::
CLEAN PREFIX-MERGE RECOVERY EQUIVOCATION
```

## Frozen v66-recoverable geometry

Every recoverable v66 scenario has:

```text
first quarantine overlap = 1
↓
2 clean identities remain
```

Those two identities are exactly the full remaining `2 / 3` shared-parent authority.

If both clean voters authorize both merge targets:

```text
AB clean cert :: valid
AC clean cert :: valid
```

then both clean voters have equivocated.

The second quarantine therefore yields:

```text
remaining clean authority
::
EMPTY
```

so neither clean merge branch remains authorized.

## Certification

- v66-recoverable scenarios: 6
- double clean prefix-merge authorizations: 6
- branch-head collisions: 0
- same-tail tests: 6
- silent rejoins: 0
- exact clean-equivocator sets: 6
- clean-equivocator set errors: 0
- aggregate remaining clean authority: 0
- AB surviving second quarantine: 0
- AC surviving second quarantine: 0
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
- second-quarantine nonempty failures: 0

**RESULT: 0e / PASS**

## Frozen consequence

```text
CLEAN PREFIX-MERGE RECOVERY
cannot bypass
PREFIX-MERGE FORK SAFETY
```

and:

```text
two conflicting fresh 2/3 prefix-merge authorizations
from same recovery epoch
::
second prefix-merge equivocation quarantine
::
clean authority = EMPTY
::
SAFE HALT
```

Both clean recovery branch histories remain evidence.

No winner is selected.

**STATUS: FROZEN / 0e / APPEND-ONLY DESCENDANTS**
