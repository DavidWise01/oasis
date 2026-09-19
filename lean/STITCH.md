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

Canonical candidate is now `Oasis.Stargate.01.lean`.
It avoids `List.get!` entirely and proves the hinge through exact list shape.
`Oasis.Stargate.00.lean` is superseded and should not be used for new tests.

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

Pending user Lean confirmation:
- Oasis.FullO.00
- Oasis.PocketPrime.00
- Oasis.Stargate.01

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
