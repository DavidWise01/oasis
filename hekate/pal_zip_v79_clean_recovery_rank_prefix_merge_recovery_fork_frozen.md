# PAL-ZIP v79 — CLEAN RECOVERY-RANK PREFIX-MERGE RECOVERY FORK PROTECTION — FROZEN

**Parent:** PAL-ZIP v78  
**State:** FROZEN / 0e  
**Scope:** prevent clean post-quarantine recovery from recreating the same recovery-prefix merge fork.

## Target

v78 permits fresh clean recovery only from the exact v77 quarantine-derived epoch.

v79 attacks that recovery path itself:

```text
same fresh recovery epoch
+
same clean exact recovery-prefix parent A
+
fresh authorize MERGE2(A,B)
+
fresh authorize MERGE2(A,C)
```

Both recovery branches can individually satisfy the original `2 / 3` threshold.

That must produce a second recovery-prefix merge equivocation and safe halt.

## Frozen clean recovery equivocation

```text
same clean voter
+
same exact recovery-prefix parent
+
same recovery epoch
+
approve peer B / merge AB
+
approve peer C / merge AC
+
AB != AC
::
CLEAN RECOVERY-RANK PREFIX-MERGE EQUIVOCATION
```

## Frozen v78-recoverable geometry

Every recoverable v78 scenario has:

```text
first quarantine overlap = 1
↓
2 clean identities remain
```

Those two identities are the complete remaining `2 / 3` authority set.

If both clean identities authorize both merge targets:

```text
AB clean cert :: valid
AC clean cert :: valid
```

then both have equivocated.

The second quarantine therefore yields:

```text
remaining clean authority
::
EMPTY
```

and neither clean merge branch remains authorized.

## Certification

- v78-recoverable scenarios: 6
- double clean merge authorizations: 6
- branch-head collisions: 0
- same-tail tests: 6
- silent rejoins: 0
- exact clean-equivocator sets: 6
- clean-equivocator errors: 0
- aggregate remaining clean authority: 0
- AB surviving second quarantine: 0
- AC surviving second quarantine: 0
- certificate ordering tests: 24
- certificate ordering failures: 0
- different-epoch controls: 3
- different-epoch false equivocation: 0
- same-merge repeat controls: 3
- same-merge repeat false equivocation: 0
- different-parent controls: 3
- different-parent false equivocation: 0
- first-quarantined identity reuse attacks: 6
- first-quarantined identity false accepts: 0
- second-quarantine nonempty failures: 0
- second-quarantine threshold checks: 6
- second-quarantine threshold failures: 0

**RESULT: 0e / PASS**

## Frozen consequence

```text
CLEAN RECOVERY-RANK PREFIX-MERGE RECOVERY
cannot bypass
RECOVERY-PREFIX FORK SAFETY
```

and:

```text
two conflicting fresh 2/3 authorizations
from same v78 recovery epoch
::
second recovery-prefix merge equivocation
::
second quarantine
::
clean authority = EMPTY
::
SAFE HALT
```

Both clean recovery branch histories remain evidence.

No winner is selected.

**STATUS: FROZEN / 0e / APPEND-ONLY DESCENDANTS**
