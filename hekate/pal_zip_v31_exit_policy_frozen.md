# PAL-ZIP v31 — EXPLICIT EXIT AUTHORIZATION POLICY BIND — FROZEN

**Parent:** PAL-ZIP v30  
**State:** FROZEN / 0e  
**Scope:** formal authorization policy binding after the exit-conflict gate.

## Target

v30 answers only:

```text
is there an exit conflict?
```

v31 keeps that separate from:

```text
is this conflict-free exit actually authorized?
```

## Frozen policy object

```text
EXIT-POLICY
::
sorted eligible source identities
+
threshold
```

No threshold is silently chosen by the kernel.

The test suite exercised three explicit policies over `T0 T1 T2`:

```text
1 / 3
2 / 3
3 / 3
```

The policy identity changes when the threshold changes.

## Frozen vote

```text
EXIT-VOTE
::
voter
+
exact policy
+
halt_head
+
action
+
target
+
decision
```

## Evaluation order

```text
EXIT CONFLICT GATE
↓
if conflict -> BLOCK

else
↓
POLICY-BOUND VOTE CHECK
↓
threshold satisfied ?
```

So:

```text
CONSISTENT EXIT
!=
AUTHORIZED EXIT
```

and:

```text
ENOUGH VOTES
cannot override
an unresolved exit conflict
```

## Certification

- explicit policies tested: 3
- approval subsets tested: 24
- subset mismatches: 0
- wrong-policy attacks: 2
- wrong-policy false accepts: 0
- wrong-proposal attacks: 2
- wrong-proposal false accepts: 0
- duplicate-voter attacks: 2
- duplicate-voter false accepts: 0
- outsider-vote attacks: 2
- outsider-vote false accepts: 0
- conflict-override attacks: 3
- conflict-override false accepts: 0
- policy identity collisions: 0

**RESULT: 0e / PASS**

## Frozen invariant

```text
CONFLICT-FREE
::
necessary

POLICY THRESHOLD
::
also necessary
```

Neither substitutes for the other.

**STATUS: FROZEN / 0e / APPEND-ONLY DESCENDANTS**
