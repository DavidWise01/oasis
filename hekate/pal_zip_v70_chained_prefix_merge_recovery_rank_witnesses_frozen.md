# PAL-ZIP v70 — CHAINED PREFIX-MERGE RECOVERY RANK WITNESSES — FROZEN

**Parent:** PAL-ZIP v69  
**State:** FROZEN / 0e  
**Scope:** bind every v69 rank witness to the exact preceding recovery-rank chain head.

## Target

v69 proves each individual strict recovery-authority rank decrease with an exact recomputable witness.

v70 freezes the ordered witness lineage.

Individually valid witnesses are not sufficient if they are reordered, detached, or spliced under the wrong recovery ancestry.

## Frozen chain objects

```text
PREFIX-MERGE-RECOVERY-RANK-CHAIN-ENTRY
::
previous_chain_head
+
exact v69 rank witness
```

```text
PREFIX-MERGE-RECOVERY-RANK-CHAIN-HEAD
::
previous_chain_head
+
exact v69 rank witness
```

Genesis:

```text
PREFIX-MERGE-RECOVERY-RANK-CHAIN:ROOT
```

## Frozen continuity gate

For adjacent witnesses:

```text
current.prior_head
=
previous.post_head
```

```text
current.eligible_before
=
previous.eligible_after
```

```text
current.rank_before
=
previous.rank_after
```

and:

```text
previous.status
=
ACTIVE
```

A `HALTED` witness therefore has no valid descendant in the same recovery lineage.

## Frozen distinctions

```text
VALID WITNESS
+
VALID WITNESS
!=
VALID CHAIN
```

unless the exact chain-head and state continuity both close.

Also:

```text
SAME RANK
!=
SAME AUTHORITY STATE
```

so a valid second witness from one rank-2 recovery branch cannot be transplanted beneath a different rank-2 authority state.

## Certification

- terminal paths: 6
- valid complete chains: 6
- chain links checked: 9
- chain-link failures: 0
- continuity checks: 3
- continuity failures: 0
- complete chain-head collisions: 0
- wrong-previous-chain attacks: 9
- false accepts: 0
- detached-witness attacks: 9
- false accepts: 0
- reorder attacks: 3
- false accepts: 0
- same-rank/different-state splice attacks: 6
- false accepts: 0
- terminal-extension attacks: 6
- false accepts: 0
- witness-tamper attacks: 9
- false accepts: 0
- chain-entry tamper attacks: 9
- false accepts: 0
- canonical ordering tests: 66
- ordering failures: 0

**RESULT: 0e / PASS**

## Frozen invariant

```text
CHAINED RECOVERY-RANK PROOF
::
ordered v69 witnesses
+
exact previous chain head
+
exact authority-state continuity
```

Therefore:

```text
detach(valid witness)
!=
valid chain continuation
```

```text
reorder(valid witnesses)
!=
valid chain
```

```text
splice(same rank, different authority state)
!=
valid chain
```

and:

```text
HALTED
::
no descendant
```

This proves ordered recovery-rank ancestry.

It does not select a winning merge branch.

**STATUS: FROZEN / 0e / APPEND-ONLY DESCENDANTS**
