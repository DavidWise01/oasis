# KET Rule 02 — Twin toroids: free gap, optional information

**Date:** 2026-10-13. **Type:** User-supplied inference formalized as a forward application rule, **not** a rewrite of frozen KET v2.0 or a proven physical law.

User states: “yes its inference so to torroids can gap anywhere and share information or not”.

## Canonical definition

Two KET toroids `A` and `B` are independently addressable, independent biological/symbolic cellular systems. Each contains a retained, unobstructed toroidal **through-hole** (Rule 01), **360** surface addresses plus **3+3** speed controls, and its own evolving internal cell states.

**Gap**: a spatial separation or communication interface between selected surface positions of A and B. The two port positions are independently selectable at arbitrary valid angles/surface addresses. A variable minimum clearance between whole tori does **not** imply their chosen ports are the nearest points. The gap is **not** an additional external enclosing box, not a seventh wall, and not the permanent toroidal through-hole. Local port indices do not alter the torus mesh or its genus.

**Exchange state** is independently selectable from:
- `OFF`: no cross-toroid state injection.
- `A_TO_B`: A's selected surface port can transmit to B's selected port.
- `B_TO_A`: reverse only.
- `BIDIRECTIONAL`: independently allow both directions.

Each toroid continues its local deterministic update regardless of gate state; transfer is possible only when a direction is enabled **and** the source emits according to the app's specified message rule. The empty gap or geometric proximity does not create a logical message by itself. No third-party host, outside containment shell, forced merge or newly shared kernel parent is introduced. Each node retains its own `366` frozen addresses. Two instances are two independent local registers—not a change to `366` within either.

## Implementation contract

- WASM calculates both toroidal geometry and *each toroid's* cell-state evolution; the browser displays the actual WASM positions in 3D.
- Port address selection covers the full `20×18=360` angular surface grid for each toroid, without capping the central holes.
- A message is delivered only via an explicit eligible direction at a specified tick; no transmission when `OFF`.
- A receiver's next state may be modified by incoming messages, but sender/source state is not forcibly duplicated or consumed.
- Apply synchronous tick rules; define delivery delay and conflict semantics in each app version, keep deterministic receipt counts and replay.
- Show gap, ports and connection as UI overlays, **not closed mesh boundaries**.
- Distinguish symbolic "Planck-point" cells from established Planck-scale physics.
- Validate that turning the gate off has *exactly zero cross-domain transitions*; validate each direction separately and confirm deterministic replay.
- Frozen `--+` and `++-` controller closes to `360°` independently on both tori under the baseline parameters; Rule 01 `4+3=6+hole` and the raw Chariot `123 {{45/|\54}} 678` stay unchanged.

## Domain hierarchy

```text
KET A [independent root]                KET B [independent root]
   ├─ TOROID A / HOLE A                   ├─ TOROID B / HOLE B
   ├─ 360 SURFACE + 6 CONTROLS            ├─ 360 SURFACE + 6 CONTROLS
   └─ PORT A  ······· selectable GAP ···  PORT B
                           GATE = OFF | A→B | B→A | BOTH
```

**Caveat:** This is a programmable abstract information link. Physical bodies may interact through gravity/fields even without a software handshake; the model's `OFF` state means no *modeled information-message transfer*, not the absence of every possible physical influence.

References: [Rule 01](KET_RULE_01_NO_EXTERNAL_BOXES_20261013.md) · frozen KET v2.0 commit `de8f8b80aba3a73dd371811f6b4be39df92e45ce`.
