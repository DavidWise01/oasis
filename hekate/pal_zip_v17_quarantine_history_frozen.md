# PAL-ZIP v17 — QUARANTINE EVENT IN APPEND-ONLY HISTORY — FROZEN

**Parent:** PAL-ZIP v16  
**State:** FROZEN / 0e  
**Scope:** formal quarantine provenance.

## Target

v16 quarantines contradictory authority without deleting the contradictory votes.

v17 makes that consequence itself auditable:

```text
CONTRADICTORY VOTES
::
remain evidence

QUARANTINE
::
new append-only event
```

## Frozen quarantine record

```text
QUARANTINE
::
prior_head
+
committee
+
sorted quarantined voter set
+
exact contradictory vote references
```

The event is canonical with respect to input ordering, but it preserves the exact
voter identities, decision context, and evidence references.

## History rule

```text
old evidence head
::
unchanged

new state
::
append(old evidence head, QUARANTINE)
```

So:

```text
QUARANTINE
!=
rewrite history

QUARANTINE
=
append consequence to history
```

## Certification

- conflicting scenarios: 6
- quarantine events built: 6
- evidence histories preserved: 6
- evidence-preservation failures: 0
- canonical permutation tests: 12
- permutation failures: 0
- context mutation tests: 12
- context mutations that preserved event identity: 0
- evidence-ref mutation tests: 12
- evidence-ref mutations that preserved event identity: 0
- quarantine-set mutation tests: 12
- quarantine-set mutations that preserved event identity: 0
- append-prefix preserved: 6
- append-prefix failures: 0
- new-context misapplication tests: 12
- new-context false applications: 0

**RESULT: 0e / PASS**

## Frozen invariant

```text
EVIDENCE
::
immutable ancestry

QUARANTINE
::
derived authority consequence

PROVENANCE
::
contains both
```

A quarantine event is scoped to the exact prior head and committee that produced it.
It does not automatically carry into another head or authority configuration.

## Stack

```text
v15 :: conflicting 3/4 exposes equivocation
v16 :: quarantine equivocating authority, preserve votes
v17 :: append quarantine consequence without erasing evidence
```

**STATUS: FROZEN / 0e / APPEND-ONLY DESCENDANTS**
