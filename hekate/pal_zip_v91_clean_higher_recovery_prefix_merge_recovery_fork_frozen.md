# PAL-ZIP v91 — CLEAN HIGHER-RECOVERY PREFIX-MERGE RECOVERY FORK PROTECTION — FROZEN

**Parent:** PAL-ZIP v90  
**State:** FROZEN / 0e  
**Scope:** prevent clean post-quarantine higher-recovery prefix merge recovery from recreating the fork.

## Target

v90 permits fresh clean recovery only from the exact v89 quarantine-derived recovery epoch.

v91 attacks that recovery path itself:

```text
same fresh recovery epoch
+
same clean exact higher-recovery prefix parent A
+
fresh authorize MERGE2(A,B)
+
fresh authorize MERGE2(A,C)
```

Both clean recovery branches may individually satisfy the original `2 / 3` threshold.

That must produce a second higher-recovery prefix-merge equivocation and safe halt.

## Frozen clean recovery equivocation

```text
same clean voter
+
same exact higher-recovery prefix parent
+
same recovery epoch
+
approve peer B / merge AB
+
approve peer C / merge AC
+
AB != AC
::
CLEAN HIGHER-RECOVERY PREFIX-MERGE EQUIVOCATION
```

## Frozen v90-recoverable geometry

Every recoverable v90 scenario has:

```text
first quarantine overlap = 1
↓
2 clean identities remain
```

Those two identities are the complete remaining authority set capable of meeting the frozen `2 / 3` threshold.

If both identities freshly authorize both convergence targets:

```text
AB clean cert :: valid
AC clean cert :: valid
```

then both remaining clean identities have equivocated.

The second quarantine therefore yields:

```text
remaining clean authority
::
EMPTY
```

and neither clean higher-recovery merge branch remains authorized.

## Certification

- v90-recoverable scenarios: 6
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
CLEAN HIGHER-RECOVERY PREFIX-MERGE RECOVERY
cannot bypass
HIGHER-RECOVERY PREFIX-FORK SAFETY
```

and:

```text
two conflicting fresh 2/3 authorizations
from same v90 recovery epoch
::
second higher-recovery prefix-merge equivocation
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
