# KET Rule 01 — NO EXTERNAL BOXES; SIX BOUNDARIES + ONE HOLE

**Issued:** 2026-10-13. **Clarified by user:** 2026-10-13.
**Status:** Authoritative forward-design rule for future 3D WASM applications; frozen KET v2.0 bytes unchanged.

## Exact source and correction

Initial user rule:

> first rule, no external boxes on ket

User's correcting explanation:

> its means if you add 4 to 3 you get 6 + a fucking hole so

**The earlier description reduced the rule to 'KET cannot be enclosed in an external box.' That missed the primary structural arithmetic. This revision supersedes that interpretation.**

### Canonical mnemonic

```text
          4 + 3 = 7
              |
          6 + 1
         /     \
   SIX BOUNDARIES   ONE HOLE
        |              |
  boundary structure   retained opening / void
         \            /
            K.E.T.
```

- **4 + 3 = 7 = 6 + 1** is the *symbolic count*.
- Six slots describe the boundary surfaces; the seventh is the **hole**, **not** another face, box, material cell, filled point, carrier, wall, or secondary shell.
- **No external boxes on KET** means do not add another six-faced cage/outer boundary to make the seventh slot 'solid', do not cap the through-opening, and do not misidentify its hole as a missing object needing an external container.
- The hole is **part of the definition** of this geometric structure; it is not an error state, a missing boundary, or an extra KET address.

### Precise geometric caveat

A cube or ordinary six-faced solid has no through-hole merely because its faces are counted. To draw the user's **toroidal** interpretation, the 3D model must visibly retain a passage through its shape (a genus-one toroidal opening). The seven-slot mnemonic alone does not prove genus one; **mesh connectivity** must realize the hole. Six 'boundaries' here is the user's symbolic accounting, not a literal mathematical statement that a smooth torus has exactly six polygonal faces.

### Keep independent counting systems independent

```text
RULE 01         4+3 = 6 boundaries + 1 HOLE  (symbolic geometry)
FROZEN REGISTRY 20×18=360 surface ports + 3+3 control ports = 366
CONTROL WORDS   --+   ++-
STATE CHANNELS  7 ordered amplitudes + 3 carriers + pinned zero
```

These counts have different domains. In particular:
- Six *symbolic faces* are **not** the six speed-control addresses.
- The structural hole is **not** a new amplitude, carrier, control address, second zero, or additional kernel cubit.
- Keep dual Greens A2/A6 separate and preserve the exact Green Chariot `123 {{45/|\54}} 678`.
- Derived cellular subdivisions are inside the toroidal model and do not allocate new frozen addresses.
- HTML cards, screen rectangles, and WASM linear-memory buffers are **display/execution tooling**, not geometric KET boxes.

### Rule 01 acceptance for future 3D WASM releases

1. The toroid has a visually and topologically **open central passage**; do not fill it with a center cell, lid, cap, cube, outer shell, or parent enclosure.
2. The 3D geometry, its scene hierarchy, and any blueprint depict **one KET toroidal body** with its opening preserved.
3. Record the symbolic rule exactly as **4+3=7=6+hole**; do not recast it as seven solid walls.
4. Preserve the **366-address frozen controller**, exact `--+` / `++-` order, final 360° closure, the other immutable glyphs, and the freeze pin.
5. Do not claim the symbolic number relation proves a physical universe, mathematical topology without a connected mesh, or Planck-scale physics.

## Model diagram

```text
               K.E.T.  [one toroidal body]
                /                   \
       boundary structure      THROUGH-HOLE
         six mnemonic slots    seventh mnemonic slot
                \                   /
                  [derived cells]
                         |
                    [3D WASM I/O]
```

The application can still contain ordinary interface panels and externally invoked code. **There is no *additional enclosing model-space box*, and the hole remains open.** In the previous Rule 01, the no-external-parent interpretation was useful as a corollary, not the main definition.

## Historical protection

- Freeze-pinned KET v2.0 commit: `de8f8b80aba3a73dd371811f6b4be39df92e45ce`.
- No changes to frozen v2.0 source files or earlier v0.2 artifacts; this correction is an additive documentation update in the forward application policy.
- Future geometry changes go into a new versioned 3D WASM application. A browser-side scene can be audited separately from the kernel itself.
