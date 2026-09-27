# PAL-ZIP v103 — CLEAN HIGHER-RECOVERY RANK-PREFIX RECOVERY-FORK PROTECTION — FROZEN

**Parent:** PAL-ZIP v102  
**State:** FROZEN / 0e  
**Scope:** prevent clean post-v101 higher-recovery rank-prefix recovery from recreating the fork.

## Target

v102 permits fresh clean recovery only from the exact v101 quarantine-derived recovery epoch.

v103 attacks that recovery path itself:

```text
same fresh v102 recovery epoch
+
same clean exact rank-prefix parent A
+
fresh authorize MERGE2(A,B)
+
fresh authorize MERGE2(A,C)
```

Both clean recovery branches may individually satisfy the frozen `2 / 3` threshold.

That must produce a second clean rank-prefix merge equivocation and safe halt.

## Frozen clean recovery equivocation

```text
same clean voter
+
same exact higher-recovery rank-prefix parent
+
same recovery epoch
+
approve peer B / merge AB
+
approve peer C / merge AC
+
AB != AC
::
CLEAN HIGHER-RECOVERY RANK-PREFIX MERGE EQUIVOCATION
```

## Frozen v102 recoverable geometry

Every recoverable v102 scenario has:

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

Append:

```text
CLEAN-HIGHER-RECOVERY-RANK-PREFIX-MERGE-SECOND-QUARANTINE
::
exact v101 quarantine head
+
exact v102 recovery epoch
+
exact clean equivocator set
+
both conflicting clean authorized-merge references
```

The second quarantine yields:

```text
remaining clean authority
::
EMPTY
```

so neither clean rank-prefix merge branch remains authorized.

## Certification

- v102-recoverable scenarios: 6
- double clean merge authorizations: 6
- branch-head collisions: 0
- same-tail tests: 6
- silent rejoins: 0
- exact clean-equivocator sets: 6
- clean-equivocator errors: 0
- second-quarantine events: 6
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
- second-quarantine context tamper attacks: 12
- context tamper same-event results: 0

**RESULT: 0e / PASS**

## Frozen consequence

```text
CLEAN HIGHER-RECOVERY RANK-PREFIX RECOVERY
cannot bypass
RANK-PREFIX FORK SAFETY
```

and:

```text
two conflicting fresh 2/3 authorizations
from same v102 recovery epoch
::
second clean rank-prefix merge equivocation
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
