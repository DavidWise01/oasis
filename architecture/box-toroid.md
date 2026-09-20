# Box / Toroidal Architecture — primitive interpretation

This document uses **box** and **toroid** as software/architecture metaphors.

```text
                      RETURN / WITNESS
                 ┌────────────────────────┐
                 │                        │
[Alice / Source] ├→ encode → [ BOX ] → decode ├→ [Bob / Destination]
                 │            │           │
                 │            │           │
                 └──── witness/error/ack ─┘
```

## BOX

A box is a boundary with explicit ingress, state, rules, and egress.

```text
BOX := {
  ingress,
  parser/decoder,
  internal state,
  allowed transforms,
  witness/log,
  egress
}
```

A useful box must make **what crosses the boundary** explicit.

## TOROID

The toroid is the closed feedback path:

```text
source → transformation → destination → witness → source
```

The forward path moves state.  
The return path confirms, rejects, repairs, or records it.

This pattern appears at different scales:

```text
transistor output → next gate → measured state → control loop
packet → receiver → ACK → sender
write → media → readback/integrity → writer
method call → callee → return/exception → caller
person → room/path → use/feedback → rearrangement
artwork → viewer → perception/critique → artist
```

## Hard-drive isolation ladder

These are **not equivalent** isolation levels:

```text
L0  directory / file permissions
L1  filesystem read-only
L2  partition / volume / namespace boundary
L3  full-volume encryption + separate key boundary
L4  device offline / driver unbound
L5  separate controller / IOMMU-DMA boundary
L6  physical write blocker or removed data path
L7  power removed / physical removal / separate host
L8  sanitization or destruction when the goal is disposal, not reuse
```

Important distinctions:

- A **partition is organization**, not strong isolation.
- Read-only software state protects against ordinary writes, not every privileged or hardware path.
- Encryption protects confidentiality while the key boundary remains intact.
- IOMMU/VFIO can constrain DMA-capable devices, but actual isolation depends on hardware topology/IOMMU groups.
- Air-gapping is a network/data-path property; it does not sanitize media.
- Sanitization is a lifecycle/disposal control, not a runtime isolation substitute.

The architecture goal is to choose the **lowest layer that actually blocks the threat/path you care about**, then witness that boundary.

## KANA cross-layer carrier

```text
+ k < | A | /\ | N | /\/ | A | /\ | >-K
```

KANA sits orthogonally across the existing box/toroid model:

```text
          +k
           │
Alice →  |A|  → transform
           │
          |N|  invariant / witness
           │
        transform → |A| → Bob
                       │
                      -K
                       │
             witness / return
```

The box bounds the transform. The toroidal return path verifies it. KANA states what must be preserved while crossing the box.

This use of "entangled" is symbolic/software architectural coupling: bindings share one invariant and are checked together.
