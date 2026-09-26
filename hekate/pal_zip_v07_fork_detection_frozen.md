# PAL-ZIP v07 — FORK DETECTION / NO SILENT REJOIN — FROZEN

**Parent:** PAL-ZIP v06  
**State:** FROZEN / 0e  
**Scope:** formal append-only history divergence.

## Target

Once `e|r` records are chained, two histories may share a prefix and then diverge.

v07 certifies that the exact chained heads identify the divergence point and that a later identical tail cannot erase the fork.

## Geometry

```text
shared prefix
::
H0 -> H1 -> H2 -> ...

fork
::
                /-> A[k] -> same tail ...
... -> H[k-1]
                \-> B[k] -> same tail ...
```

Because every head contains the previous head:

```text
history before the current entry
::
is part of the current identity
```

Therefore:

```text
same later payload
!=
same history
```

after a fork.

## Fork locator

Compare prefix heads in order.

```text
first unequal head index
::
fork index

number of equal prefix heads
::
length of common history
```

## Certification

Baseline entries: `32`

### Single fork at every position

- fork cases: `32`
- exact fork index: `32`
- fork index errors: `0`

### Same tail after divergence

- cases: `32`
- false silent rejoins: `0`

### Same prefix, different new append streams

- cases: `32`
- false equal final heads: `0`

### Truncation

- cases: `33`
- exact common-prefix results: `33`

**RESULT: 0e / PASS**

## Frozen invariant

```text
FORK
::
once H_A[k] != H_B[k]

then
::
later equal pair payloads
do not make the exact heads equal again
```

So:

```text
SAME CONTENT LATER
!=
SAME PROVENANCE
```

## DACI relevance

This gives the distributed layer a minimal primitive:

```text
same head
::
same represented history

different head
::
histories differ

prefix-head scan
::
find first divergence
```

No winner is chosen by this primitive. It only exposes the fork deterministically.

## Contract stack

```text
v03 :: e identity
v04 :: r identity
v05 :: e|r pair bind
v06 :: append-only trusted head
v07 :: fork detection / no silent rejoin
```

**STATUS: FROZEN / 0e / APPEND-ONLY DESCENDANTS**
