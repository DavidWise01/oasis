# PAL-ZIP v58 — CHAINED MERGE-AUTHORITY RANK WITNESSES — FROZEN

**Parent:** PAL-ZIP v57  
**State:** FROZEN / 0e  
**Scope:** bind individually valid merge-authority rank witnesses into one exact terminating history.

## Target

v57 proves one merge-authority rank decrease is valid.

v58 prevents individually valid v57 witnesses from different merge histories from being
spliced into a fake monotone chain.

## Frozen chain entry

```text
MERGE-RANK-CHAIN-ENTRY
::
previous_chain_head
+
exact MERGE-AUTH-RANK-WITNESS
```

The next chain head is:

```text
MERGE-RANK-CHAIN-HEAD
::
previous_chain_head
+
exact MERGE-AUTH-RANK-WITNESS
```

## Frozen continuity

For every non-genesis witness:

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

A terminal `HALTED` witness cannot have a descendant.

## Same rank is not enough

The principal splice attack uses two distinct first quarantines:

```text
branch A
::
rank 3 -> rank 2
eligible_after = state A

branch B
::
rank 3 -> rank 2
eligible_after = state B
```

Although both branches have rank `2`:

```text
state A != state B
```

Therefore the second witness from branch B cannot be appended after branch A.

Frozen distinction:

```text
SAME RANK
!=
SAME STATE
```

and:

```text
VALID WITNESS
+
VALID WITNESS
!=
VALID CHAIN
```

## Certification

- terminal v56 paths: 6
- valid chain links: 9
- valid chain-link failures: 0
- valid complete chains: 6
- complete-chain-head collisions: 0
- same-rank/different-state splice attacks: 6
- splice false accepts: 0
- wrong previous-chain attacks: 3
- false accepts: 0
- wrong prior-head attacks: 3
- false accepts: 0
- wrong eligible-before attacks: 3
- false accepts: 0
- terminal-extension attacks: 6
- false accepts: 0
- witness-tamper attacks: 9
- false accepts: 0
- chain-entry tamper attacks: 9
- false accepts: 0
- canonical ordering tests: 54
- ordering failures: 0

**RESULT: 0e / PASS**

## Current geometry

```text
MERGE AUTHORITY
      |
      v
RANK-WITNESS W1
      |
      v
CHAIN-HEAD H1
      |
      v
RANK-WITNESS W2
      |
      v
CHAIN-HEAD H2
      |
      v
HALTED
```

Each descendant commits to the exact prior chain and exact prior merge-authority state.

**STATUS: FROZEN / 0e / APPEND-ONLY DESCENDANTS**
