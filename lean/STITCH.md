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

Canonical checkpoint: `Oasis.Duality.Exception.05.lean` (user-confirmed silent `0e`).

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

`Oasis.Duality.Exception.00.lean` through `.04` are superseded compatibility attempts. `05` uses an exact algebraic quarter-step carrier, avoiding version-specific integer-normalization behavior.

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
- Oasis.NEON3.00
- Oasis.Duality.Exception.05

Pending user Lean confirmation:
- Oasis.FullO.00
- Oasis.PocketPrime.00

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


## OaSIs v00 Full Emergent — 2026-09-19

`Oasis.Duality.Exception.05.lean` is user-confirmed silent `0e` and supersedes `.00` through `.04`.

The v00 clean stitch contains 17 user-confirmed checkpoints:

```text
Cube.00
OSI1.00 .. OSI7.00
OSI8.HACI.00
OSI9.00
OSI0.Provenance.00
OSI0.CreativeSubstrate.00
GeoSub.OSI.v02_1
Arch.00
Stargate.02
NEON3.00
Duality.Exception.05
```

`Oasis.v00.FullEmergent.lean` is the new standalone convergence candidate. It records the clean ledger and proves the shared closure constants without promoting historically pending modules.

The root GitHub page is the v00 emergent portal:

```text
Root0 -> Stargate -> NEON^3 -> Duality -> PER/CEPT/ION -> Art Workstation
```

The root page intentionally replaces the previous CFI/obligation presentation so the public surface tracks the current deterministic creative architecture rather than stale claims.


## Full clean package classification — 2026-09-19

User reports all current canonical Lean targets clean through `Oasis.v00.FullEmergent.lean`.
Previously pending `Oasis.FullO.00.lean` and `Oasis.PocketPrime.00.lean` are therefore promoted to the clean package.

Delimiter taxonomy:

```text
|    ISO / deterministic machine stack
||   human / carbon / provenance attachment
|||  full NEON engine
```

Operational `|||` package levels:

```text
|||.0 GATE          Stargate.02
|||.1 STRUCTURE     NEON3.00
|||.2 EXCEPTION     Duality.Exception.05
|||.3 POCKET        PocketPrime.00
|||.4 ORCHESTRATOR  FullO.00
|||.5 EMERGENT      v00.FullEmergent
|||.6 ART SURFACE   workstation/
|||.7 PUBLIC PORTAL GitHub Pages root
```

Full class map: `docs/OASIS_V00_CLASSMAP.md`.


## O^1 immutable freeze + public A attachment — 2026-09-19

The current user-verified Lean-clean stack is frozen as:

```text
O^1 = ||| OaSIs |||
```

Canonical freeze manifest:
- `Oasis.O1.Immutable.00.lean`
- 21 verified-clean canonical Lean artifacts are recorded in the release ledger.
- O^1 is free and append-only by release convention; descendants attach instead of mutating the frozen manifest.

Public application socket:

```text
||| A |||
```

Canonical attachment module:
- `Oasis.A.PublicAttachment.00.lean`
- parent: `O^1`
- parent source SHA-256: `a3558280434a300008a4fde47718f9216f353593701038811c70e28f115d5c09`
- `parentMutable = false`
- `free = true`
- `public = true`
- domain remains `UNBOUND` until a descendant application is attached.

Inherited stack:
Root0, provenance, lineage, private Stargate, math engine, Duality, PER/CEPT/ION, private/public membrane, local project state, and export surface.

The first intended descendant probe is Tattoo Generator, but the tattoo engine is not part of the frozen A socket.

New wrapper status: source generated and published; local Lean confirmation of these two new wrapper modules is still required before labeling the wrappers themselves `0e`.


## O3 freeze — 2026-09-20

Canonical name: **O3**.

User-confirmed silent Lean `0e`.

```text
lean/O3.lean
```

Canonical source SHA-256:

```text
9ed23de7504fc284af95d4c39209a754d40886c0909d7d15c9121ff683e4d282
```

Frozen invariants:

```text
0 .
├── 0.1 ..
└── 0.2 ...

outputs          = 2
nodes            = 3
isomorph width   = 6
verify count     = 2
verify envelope  = 20
```

The historical filename `Oasis.GroundTruth.MitosisIso.00.lean` remains provenance only. `O3` is immutable by release convention; descendants append rather than modify it.

## MORE GARBAGE primitive-scope correction — 2026-09-20

`Oasis.MoreGarbage.00.lean` is retained as provenance but its whole-object scope is superseded.

Fresh candidate:

```text
Oasis.MoreGarbage.01.lean
```

v01 formalizes:

```text
Y → +1 → move on
N → (0,0,0,-1) down → search
scan cost = n
search model = n × n = n²
rm / A::xx = delete current + move forward
```

Primitive-scope runtime regression: **6/6 PASS**.

Lean v01 remains pending user `0e` confirmation.


## MORE GARBAGE one-bit reverse recursion correction — 2026-09-20

`Oasis.MoreGarbage.Prim1Bit.00.lean` is preserved as provenance but its forward 1..8 schedule is superseded.

Fresh descendant:

```text
Oasis.MoreGarbage.Prim1Bit.01.lean
```

Current encoded invariants:

```text
primitive signature = [1 1 2 4] . n . n²

find moji
  ↓
8
↓
3
↓
2
↓
1

recursive anchor = 0.[O].0

unresolved → recurse
Y → repair
N → no repair

cohesion seed = literal 1.1 of a nibble
Y may cohere from 1.1
N may still cohere from 1.1
```

The N branch does not claim recovery of the original primitive.

Lean status: **pending user 0e confirmation**.
