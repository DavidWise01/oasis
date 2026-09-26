# PAL-ZIP v41 — POST-FORK CLEAN ROTATION RECOVERY — FROZEN

**Parent:** PAL-ZIP v40  
**State:** FROZEN / 0e  
**Scope:** clean recovery after certified rotation equivocation quarantine.

## Target

After v39/v40:

```text
certified rotation fork
↓
rotation equivocation
↓
ROTATION-QUARANTINE
```

a new rotation may proceed only from the **quarantine head** using a **fresh quorum**
composed entirely of non-quarantined parent-policy voters.

## Frozen recovery rule

```text
eligible recovery voter
::
parent-policy member
-
rotation-quarantine set
```

and:

```text
fresh vote
::
quarantine_head
+
parent
+
child
+
decision
```

The original parent threshold is preserved.

For the frozen parent:

```text
P2
::
2 / 3
```

so recovery still requires `2`.

## Exhaustive 2-of-3 fork geometry

There are nine possible conflicting quorum-pair scenarios.

Two cases occur:

```text
intersection size = 1
↓
2 clean voters remain
↓
fresh 2/3 recovery possible
```

or:

```text
intersection size = 2
↓
1 clean voter remains
↓
threshold cannot be met
↓
SAFE HALT
```

## Certification

- fork scenarios: 9
- expected recoverable scenarios: 6
- actual recoverable scenarios: 6
- expected safe halts: 3
- actual safe halts: 3
- recoverability mismatches: 0
- old-head vote replay attacks: 6
- old-head vote replay false accepts: 0
- quarantined-vote substitution attacks: 6
- quarantined-vote false accepts: 0
- old-certificate replay attacks: 6
- old-certificate replay false accepts: 0
- certificate voter-order tests: 12
- certificate order failures: 0
- wrong-child attacks: 6
- wrong-child false accepts: 0
- wrong-parent attacks: 6
- wrong-parent false accepts: 0
- append-prefix tests: 6
- append-prefix failures: 0

**RESULT: 0e / PASS**

## Frozen invariant

```text
OLD ROTATION CERT
!=
FRESH RECOVERY AUTHORITY
```

and:

```text
QUARANTINED VOTE
::
cannot carry forward
```

and:

```text
RECOVERY
::
fresh head
+
fresh clean voters
+
original parent threshold
```

If too few clean parent-policy voters remain, v41 does not weaken the threshold.
It remains safely halted.

**STATUS: FROZEN / 0e / APPEND-ONLY DESCENDANTS**
