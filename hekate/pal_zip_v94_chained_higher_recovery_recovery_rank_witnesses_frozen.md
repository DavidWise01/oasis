# PAL-ZIP v94 — CHAINED HIGHER-RECOVERY RECOVERY-RANK WITNESSES — FROZEN

**Parent:** PAL-ZIP v93  
**State:** FROZEN / 0e  
**Scope:** bind each valid v93 higher-recovery recovery-rank witness to the exact preceding witness-chain head.

## Target

v93 proves each individual higher-recovery quarantine transition with an exact recomputable rank witness.

v94 prevents valid individual witnesses from being:

```text
detached
reordered
spliced
or transplanted
```

across different higher-recovery authority histories.

## Frozen chain entry

```text
HIGHER-RECOVERY-PREFIX-MERGE-RECOVERY-RANK-CHAIN-ENTRY
::
previous_chain_head
+
exact v93 rank witness
```

## Frozen chain head

```text
HIGHER-RECOVERY-PREFIX-MERGE-RECOVERY-RANK-CHAIN-HEAD
::
previous_chain_head
+
exact v93 rank witness
```

Genesis:

```text
HIGHER-RECOVERY-PREFIX-MERGE-RECOVERY-RANK-CHAIN:ROOT
```

## Frozen continuity

For witness `W(n+1)` to follow `W(n)`:

```text
W(n+1).prior_head
=
W(n).post_head
```

```text
W(n+1).eligible_before
=
W(n).eligible_after
```

```text
W(n+1).rank_before
=
W(n).rank_after
```

and:

```text
W(n).status
=
ACTIVE
```

A `HALTED` witness has no valid descendant in the same recovery chain.

## Frozen distinction

```text
VALID WITNESS
+
VALID WITNESS
!=
VALID CHAIN
```

unless exact state continuity and exact previous-chain provenance both hold.

Also:

```text
SAME RANK
!=
SAME HIGHER-RECOVERY AUTHORITY STATE
```

## Certification

- terminal paths: 6
- valid chains: 6
- chain links: 9
- chain-link failures: 0
- state-continuity checks: 3
- state-continuity failures: 0
- rank-continuity checks: 3
- rank-continuity failures: 0
- final chain-head collisions: 0
- wrong-previous-head attacks: 9
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
- chain-entry-tamper attacks: 9
- false accepts: 0
- canonical-order tests: 66
- canonical-order failures: 0

**RESULT: 0e / PASS**

## Frozen invariant

```text
VALID v93 WITNESS
::
local proof
```

```text
VALID v94 CHAIN
::
local proof
+
exact prior chain head
+
exact authority-state continuity
+
exact rank continuity
```

Therefore:

```text
VALID WITNESS + VALID WITNESS
!=
VALID CHAIN
```

and:

```text
SAME RANK
!=
SAME HIGHER-RECOVERY AUTHORITY STATE
```

No winning branch is selected.

**STATUS: FROZEN / 0e / APPEND-ONLY DESCENDANTS**
