# PAL-ZIP v08 — TWO-PARENT MERGE / NO HISTORY ERASURE — FROZEN

**Parent:** PAL-ZIP v07  
**State:** FROZEN / 0e  
**Scope:** formal fork reconciliation.

## Target

v07 can expose a fork:

```text
          /-> HEAD_A
COMMON --<
          \-> HEAD_B
```

v08 asks how the branches can rejoin **without pretending the fork never happened**.

## Frozen merge primitive

```text
MERGE2
::
requires exactly two distinct parent heads

M
::
canonical(
  sort(HEAD_A, HEAD_B)
)
```

Sorting makes the merge representation independent of observer input order:

```text
MERGE2(A,B)
=
MERGE2(B,A)
```

while retaining both actual parent identities.

## What it does not do

```text
MERGE2
!=
choose A

MERGE2
!=
choose B

MERGE2
!=
erase the fork
```

It creates a new descendant whose provenance explicitly contains both branch heads.

## Certification

Forked the same baseline at every one of `16` positions.

- fork pairs: `16`
- swapped-parent order tests passed: `16`
- swapped-parent order failures: `0`
- parent mutation tests: `32`
- parent mutation false accepts: `0`
- duplicate-parent rejections: `16`
- one-parent rejections: `16`

**RESULT: 0e / PASS**

## Frozen invariant

```text
FORK
::
history diverges

MERGE2
::
new child references BOTH divergent heads

therefore
::
reconciliation does not rewrite ancestry
```

And:

```text
same merge payload
+
different parent head
::
different merge identity
```

## DACI projection

```text
NODE A ----\
            >---- MERGE2 ----> next append-only state
NODE B ----/
```

The merge primitive provides deterministic parent binding only.
Authority/quorum for *whether* a merge is accepted remains a separate layer.

## Contract stack

```text
v03 :: e identity
v04 :: r identity
v05 :: e|r cross-bind
v06 :: append-only external head
v07 :: fork detection
v08 :: two-parent merge preserving both histories
```

**STATUS: FROZEN / 0e / APPEND-ONLY DESCENDANTS**
