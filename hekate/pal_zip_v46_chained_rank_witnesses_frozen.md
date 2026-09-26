# PAL-ZIP v46 — CHAINED RANK WITNESSES — FROZEN

**Parent:** PAL-ZIP v45  
**State:** FROZEN / 0e  
**Scope:** bind individually valid rank witnesses into one exact monotone history.

## Target

v45 proves one `RANK-WITNESS` is internally valid.

v46 prevents an attacker from taking individually valid witnesses from different histories and
splicing them into a fake monotone chain.

## Frozen chain entry

```text
RANK-CHAIN
::
previous_chain_head
+
exact RANK-WITNESS
```

Each witness also carries an exact:

```text
pre_head
post_head
eligible_before
eligible_after
rank_before
rank_after
action
status
```

## Frozen continuity rule

For every non-genesis step:

```text
current.pre_head
=
previous.post_head
```

and:

```text
current.eligible_before
=
previous.eligible_after
```

and:

```text
previous.status
=
ACTIVE
```

A `CLOSED` or `HALTED` witness cannot have a successor.

## Frozen rank rule

```text
ACTIVE -> ACTIVE
::
rank_after < rank_before
```

Terminal transitions may preserve rank:

```text
ACTIVE -> CLOSED
ACTIVE -> HALTED
```

## Certification

- valid first steps: 1
- valid first-step failures: 0
- valid continuations: 3
- valid continuation failures: 0
- wrong previous-chain attacks: 3
- false accepts: 0
- wrong pre-head attacks: 3
- false accepts: 0
- wrong eligible-before attacks: 3
- false accepts: 0
- alternate-branch splice attacks: 1
- false accepts: 0
- terminal-successor attacks: 3
- false accepts: 0
- witness-tamper attacks: 1
- false accepts: 0
- canonical ordering tests: 6
- ordering failures: 0
- legitimate chain-head collisions: 0

**RESULT: 0e / PASS**

## Frozen invariant

```text
VALID WITNESS A
+
VALID WITNESS B
!=
VALID CHAIN
```

unless:

```text
A.post_head = B.pre_head
A.eligible_after = B.eligible_before
A.status = ACTIVE
B binds exact previous chain head
```

Therefore a valid witness from another branch cannot be imported into the current chain merely
because it is valid in isolation.

## Frozen geometry

For the current `3 identities / threshold 2` state machine:

```text
3 eligible
↓ one valid ACTIVE witness
2 eligible
↓
CLOSED
or
HALTED
```

No terminal witness can be extended.

**STATUS: FROZEN / 0e / APPEND-ONLY DESCENDANTS**
