# KET Rule 01 — NO EXTERNAL BOXES

**Date:** 2026-10-13
**Priority:** First user-defined spatial/architectural rule for the KET 3D WASM generative I/O layer.
**Source:** User instruction: "first rule, no external boxes on ket".
**Policy:** Additive forward-build rule. Does **not** rewrite or mutate the already frozen KET v2.0 kernel.

## Rule

> **NO EXTERNAL BOXES ON KET.**

KET is the root object of its model. Nothing outside the KET kernel may create, own, contain, wrap, or impose an enclosing 3D box around its root geometry.

This applies equally to scene graphs, cell-generation engines, engineering drawings, and generated diagrams.

### What is allowed

- The fixed KET 360-surface toroidal geometry and its 3+3 control ports (366 distinct addressable positions).
- **Internal** 3D cellular subdivision and emergent state inside the toroidal model, including symbolic "Planck-point" resolution when configured.
- Directly attached or read-only external input and output **ports/interfaces** that do not allocate additional kernel addresses or define a containing parent domain.
- A WebGL2 viewport, a WASM runtime, browser UI forms/panels or a JSON receipt **as application tooling**; these are *not* extra geometric shells belonging to or owning KET.
- Distinct Green A2/A6 and the exact raw Chariot glyph, without inserting enclosing "boxes" around them.

### What is forbidden

- Drawing any external cuboid, enclosing simulation boundary box, lattice cage, rectangular halo/casing, Dyson-style outer shell, or extra closed parent surface **around KET**.
- Making KET a child of an externally owned world/container/root geometry in the scene/domain model.
- Changing the kernel from 366 logical addresses because a renderer adds bounding planes.
- Conflating browser layout cards, tool windows or screen framing with new kernel layers.
- Promoting a derived cell's temporary storage buffer into a newly allocated external kernel box.

### Required 3D scene hierarchy

```text
KET  [scene/domain root]
  ├── TOROID [360 surface addresses]
  │     └── CELLULAR INTERIOR [derived transient 3D states]
  ├── CONTROLS [6 positions = --+ / ++-]
  └── IO PORTS [attached interfaces, never an enclosing volume]

VIEWER / WASM / HTML [tools observing/interacting; NOT KET geometry]
```

**Model acceptance:** the domain-root object is KET; every model-space geometry item is KET-owned and is either the toroid, its internal subdivision, or an allowed attached/non-enclosing port. No outside closed mesh encloses the torus. The scene may still be drawn in a normal rectangular browser viewport—that is not a physical/symbolic KET box.

## Enforcement on forward builds

1. Each new 3D WASM application release must document **Rule 01: PASS** or explain its noncompliance.
2. Review model geometry/scene graph for extra closed enclosing structures and for external ownership.
3. Confirm the immutable register remains **360 + 3 + 3 = 366**, and that derived cells do not become kernel addresses.
4. Preserve prior immutable symbols and results: `--+`, `++-`, `123 {{45/|\54}} 678`, seven ordered amplitudes (Green twice), White/Black/Gray carriers, pinned zero, and baseline 360° closure.
5. Do not misrepresent internal cellular simulation as established Planck-scale physics.

**Scope note:** "no external boxes" is interpreted as a **domain-geometry/ownership restriction**, not a prohibition against every rectangular browser UI element or WebAssembly memory allocation. This clarification is an implementation interpretation; the quoted user rule above remains authoritative.

## Immutable reference
- KET v2.0 freeze commit: [de8f8b80aba3a73dd371811f6b4be39df92e45ce](https://github.com/DavidWise01/oasis/commit/de8f8b80aba3a73dd371811f6b4be39df92e45ce)
- Application v0.2 remains historical, unchanged; next code revision should be additive v0.3.

