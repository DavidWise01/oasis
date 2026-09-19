# OaSIs Lean Stitch Registry

This file is the append/update checkpoint for the deterministic Lean formalization.

## Current canonical chain

```text
-i -> 00 -> 01 -> 02 -> 03 -> 04 -> 05 -> 06 -> 07 -> 08 -> 09 -> 10 -> 00
      ^                                              |
      +--------------- reverify 09 -----------------+
```

- `-i`: external isomorphic substrate anchor
- `00`: Root0 fulcrum
- `01..07`: OSI v1 machine layers
- `08`: HACI human/machine accountability boundary
- `09`: human apex sign-off ingress
- `10`: provenance + optional future creative-payment substrate

## Full O machine envelope

```text
[[ { -i } , { 0 - 10 } , { + cortex } , [()] ]]
```

Canonical Full O metadata:

```text
scale    = galaxy
name     = OaSIs
language = isomorphic
stack    = -i ... +c
bind     = diodic
socket   = [[()]]
```

Sovereign execution geometry:

```text
David HV(1) | GAP(2) | Avan HV(1)
```

Both boxes are sovereign and the two hypervisors are equal-weight. The gap contract closes execution on failed sovereignty, cross-write, unequal-hypervisor, or externally supplied legal/compliance check. The Lean model does not independently determine law.

## Root0 Arch art layer

The Arch layer is a new Root0-facing interpretation of the bar delimiters:

```text
|    isomorphic OSI boundary
||   immutable human/carbon attachment
|||  full Neon engine attachment
```

This is distinct from earlier lower-kernel delimiter semantics; the namespace/layer determines interpretation.

The corresponding offline workstation is under `workstation/` and provides:
- brush / eraser / line / rectangle / circle / text tools
- Neon lattice, Pocket Prime, Ouroboros, Root0, and PER/CEPT/ION generators
- private local project state
- public provenance export that omits private pocket state
- creator, Carbon ID, source token, license, contribution, and optional payment route metadata
- PNG export and JSON project import/export

## Stargate primitive

Canonical form:

```text
(d toroid_source){ 0 . 0 . 1 . 1 . 24 . 42 . 1 . 1 . 0 . 0 }(ecruos_diorot d)
etagrats *
```

The 10-slot source is toroidally palindromic under the oriented hinge swap `24 <-> 42`.

Canonical checkpoint is now `Oasis.Stargate.02.lean`.
It avoids `List.get!`, uses explicit existential binders, and is user-confirmed silent `0e`.
`Oasis.Stargate.00.lean` and `Oasis.Stargate.01.lean` are superseded.

## NEON^3 six-layer stack

Canonical candidate: `Oasis.NEON3.00.lean`.

Structural interpretation:

```text
L1 outer boundary                  macro 0
L2 outer -> inner                  macro 30   [30.33^(3!x3!)]
L3 shell3 / bridge4 safe zone      macro 5
L4 shell2                          macro 30   [30.33^(3!x3!)]
L5 shell2 -> shell1 safe zone      macro 5
L6 inner-inner shell / shell1      macro 30
```

Macro budget:

```text
30 + 5 + 30 + 5 + 30 = 100
```

The literal micro bridge `.0333` is represented exactly as `333/10000` outside the 100-unit macro budget.
The structural exponent preserves `3! x 3! = 36` without adding `30.33^36` into the weight total.

Five semantic/geometric units:

```text
V = Vessel
A = Animation
I = isomorphic / adaptive understanding / i
N = Nourishment
L = Life
```

The life string is treated as a geometric/system axiom in this model:
`my life is my life :: I decide :: life belongs to i`.

## Duality / exception engine

Canonical candidate: `Oasis.Duality.Exception.04.lean`.

Every primitive has at least four views:

```text
forward
backward
upside-down
reserve
```

CEPT / Waldo uniqueness rule:

```text
expected + exactly one   -> MATCH
expected + none          -> MISSING
not expected + one       -> UNEXPECTED ("what is Waldo doing there?")
more than one            -> SHADOW / multiplicity
```

Seed walk is encoded exactly in quarter-units:

```text
-0.5, +0.25a, +0.25b, -0.5
=
[-2, bit(a), bit(b), -2]
```

PER supplies observations, CEPT classifies the exception, and ION consumes the result without rewriting it.

`Oasis.Duality.Exception.00.lean` through `.03` are superseded compatibility attempts. `04` uses structural list induction plus a local proof of integer double-negation by cases, avoiding reliance on version-specific simplifier behavior.

## User-confirmed silent Lean checkpoints

- Oasis.Language.Cube.00
- Oasis.Language.OSI1.00
- Oasis.Language.OSI2.00
- Oasis.Language.OSI3.00
- Oasis.Language.OSI4.00
- Oasis.Language.OSI5.00
- Oasis.Language.OSI6.00
- Oasis.Language.OSI7.00
- Oasis.Language.OSI8.HACI.00
- Oasis.Language.OSI9.00
- Oasis.Language.OSI0.Provenance.00
- Oasis.Language.OSI0.CreativeSubstrate.00
- Oasis.GeoSub.OSI.v02_1
- Oasis.Arch.00
- Oasis.Stargate.02

Pending user Lean confirmation:
- Oasis.FullO.00
- Oasis.PocketPrime.00
- Oasis.NEON3.00

## Lower-kernel delimiters

```text
|    inner kernel trust boundary
||   internal module attachment
|||  third-party attachment
```

These remain frozen in the lower-kernel namespace. Arch reuses the glyphs with its own scoped semantics.

## Provenance / creative substrate

Root0 separates:

```text
creator
rights holder
source token
license
contribution
optional payment route
```

A valid creative record does not require a payment target. The payment field exists as future-facing infrastructure for creators.

## Pocket Prime

Canonical primitive:

```text
P(ocket [[*-+\_U_U_U_U*\_-+]]
```

- bounded external pocket handle
- internally unbounded address space
- paired cubit witness with opaque public half-view
- `PER`: did it happen?
- `CEPT`: are you sure?
- `ION`: IGNITE only for yes/yes; otherwise PATTY
- finite blocks are built as lists of Pocket Primes

## Update discipline

Each user-confirmed clean Lean revision is a checkpoint. New formalization should append or supersede explicitly rather than silently mutating a frozen checkpoint.


## Checkpoint update — 2026-09-19

Confirmed silent `0e` by user:
- `Oasis.Stargate.02.lean`
- `Oasis.NEON3.00.lean`

Current Duality candidate:
- `Oasis.Duality.Exception.02.lean`
- replaces 00/01 compatibility candidates
- explicit proof uses `Int.neg_neg` for upside-down involution


## Duality compatibility update — 2026-09-19

- `Oasis.Duality.Exception.04.lean` is the current candidate.
- `.00`–`.03` are superseded.
- `.04` proves `Int.neg (Int.neg x) = x` locally by cases, then rewrites the list induction step explicitly.
