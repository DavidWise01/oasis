# PAL-ZIP v115 — CLEAN PREFIX-MERGE RECOVERY-FORK PROTECTION — FROZEN

**Parent:** PAL-ZIP v114  
**State:** FROZEN / 0e  
**Scope:** prevent fresh post-quarantine authority from recreating the same clean higher-recovery prefix-merge fork.

## Target

v114 allows recovery only in the six scenarios where exactly two clean authority identities remain.

At the frozen `2 / 3` threshold, those two surviving clean identities are both required for every fresh post-quarantine authorization.

v115 attacks this condition:

```text
same exact v114 recovery epoch
+
same exact clean prefix parent A
+
fresh authorize MERGE2(A,B)
+
fresh authorize MERGE2(A,C)
```

Both fresh merges can individually satisfy v114.

That does not permit either branch to become canonical.

## Clean recovery equivocation

For each surviving clean identity:

```text
same voter
+
same exact parent A
+
same exact v114 recovery epoch
+
approve MERGE2(A,B)
+
approve MERGE2(A,C)
::
FRESH CLEAN PREFIX-MERGE EQUIVOCATION
```

Since exactly two clean identities remain and threshold is `2`, both clean identities must participate in both authorizations.

Therefore the clean equivocator set is exactly the full remaining clean authority.

## Second quarantine

Append:

```text
CLEAN-HIGHER-RECOVERY-PREFIX-MERGE-SECOND-QUARANTINE
::
exact v113 first-quarantine head
+
exact v114 recovery epoch
+
exact clean equivocator set
+
both conflicting fresh authorized merge refs
```

Then:

```text
remaining clean authority
=
eligible clean authority - clean equivocators
=
EMPTY
```

Therefore:

```text
SAFE HALT
```

No threshold weakening is permitted.

## Certification

- v114 recoverable scenarios: 6
- double fresh merge authorizations: 6
- double-authorization failures: 0
- branch-head collisions: 0
- same-tail tests: 6
- same-tail false rejoins: 0
- exact clean-equivocator sets: 6
- clean-equivocator-set errors: 0
- second-quarantine events: 6
- second-quarantine nonempty failures: 0
- aggregate remaining clean authority: 0
- AB survives second quarantine: 0
- AC survives second quarantine: 0
- certificate-order tests: 48
- certificate-order failures: 0
- different-epoch controls: 12
- different-epoch false equivocation: 0
- same-merge repeat controls: 12
- same-merge repeat false equivocation: 0
- different-parent controls: 12
- different-parent false equivocation: 0
- first-quarantined identity reuse attacks: 6
- first-quarantined identity reuse false accepts: 0
- second-quarantine threshold checks: 6
- second-quarantine threshold failures: 0
- second-quarantine context-tamper attacks: 12
- context tamper preserving same event: 0

**RESULT: 0e / PASS**

## Frozen consequence

```text
CLEAN POST-QUARANTINE RECOVERY
cannot bypass
PREFIX-MERGE FORK SAFETY
```

and:

```text
two conflicting fresh 2/3 authorizations
from same v114 recovery epoch
::
fresh clean prefix-merge equivocation
::
second quarantine
::
clean authority = EMPTY
::
SAFE HALT
```

Neither fresh branch is selected.

No winner is selected.

**STATUS: FROZEN / 0e / APPEND-ONLY DESCENDANTS**
