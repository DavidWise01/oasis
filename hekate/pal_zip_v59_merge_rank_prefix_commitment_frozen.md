# PAL-ZIP v59 — MERGE-RANK CHAIN PREFIX COMMITMENT — FROZEN

**Parent:** PAL-ZIP v58  
**State:** FROZEN / 0e  
**Scope:** commit every merge-rank chain head to the complete ordered v58 witness ancestry.

## Target

v58 proves adjacent merge-authority witnesses form a valid chain.

v59 freezes the full ordered prefix so a valid tail cannot be detached from its exact earlier
merge-authority ancestry.

## Frozen prefix head

```text
MERGE-RANK-PREFIX-HEAD
::
depth
+
previous_prefix_head
+
exact MERGE-RANK-CHAIN-ENTRY
```

Genesis:

```text
MERGE-RANK-PREFIX:ROOT
```

Recursive form:

```text
P1 := PREFIX(1, ROOT, C1)
P2 := PREFIX(2, P1, C2)
...
```

where `Cn` is the exact v58 chain entry containing the exact prior v58 chain head and witness.

## Frozen distinction

```text
VALID CHAIN ENTRY
!=
VALID PREFIX PLACEMENT
```

A chain entry valid on one ancestry cannot simply be grafted under another prefix.

Also:

```text
SAME RANK
!=
SAME STATE
```

remains preserved through the prefix commitment.

## Certification

- terminal histories: 6
- prefix links checked: 9
- prefix-link failures: 0
- final prefix collisions: 0
- truncation tests: 3
- truncations reproducing final head: 0
- different-prefix replacement attacks: 6
- replacement false accepts: 0
- same-prefix sibling controls: 30
- same-prefix control failures: 0
- old-prefix graft attacks: 6
- old-prefix grafts reproducing authentic head: 0
- wrong-depth attacks: 9
- wrong-depth same-head results: 0
- chain-entry tamper attacks: 9
- chain-entry tamper same-head results: 0
- same-rank/different-state tail-splice attacks: 6
- splice same-head results: 0
- canonical ordering tests: 66
- ordering failures: 0

**RESULT: 0e / PASS**

## Frozen invariant

```text
FINAL MERGE-RANK PREFIX HEAD
::
commitment to
the entire ordered v58 witness ancestry
```

Therefore:

```text
truncate(prefix)
!=
authentic final head
```

```text
replace(prefix with different ancestry)
!=
authentic head
```

```text
graft(old prefix, newer chain entry)
!=
authentic head
```

and:

```text
same rank
+
different merge-authority state
::
cannot splice
```

**STATUS: FROZEN / 0e / APPEND-ONLY DESCENDANTS**
