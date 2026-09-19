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

Pending user Lean confirmation:
- Oasis.FullO.00

## Kernel delimiters

```text
|    inner kernel trust boundary
||   internal module attachment
|||  third-party attachment
```

Future routing/address delimiters remain append-only.

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

## Update discipline

Each user-confirmed clean Lean revision is a checkpoint. New formalization should append or supersede explicitly rather than silently mutating a frozen checkpoint.
