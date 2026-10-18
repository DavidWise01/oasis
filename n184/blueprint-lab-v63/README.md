# N184 Blueprint Lab — Revision B (v6.3 visual release)

**Scope:** 3D/4D interactive engineering visualization and wiring only. The frozen v6.1 N184 mapping and recovery implementation are not modified.

## Additive commit chunks

1. `index.html` — page layout, controls, technical sheet, orthographic canvases, exports
2. `geometry.js` — exact 4D tesseract topology (16 vertices, 32 edges); all six independent 4D rotation planes; perspective/orthographic projection; nested boxes, three toroidal wireframes, line/slab filtering, reversible address mapping
3. `app.js` — 3D drag/orbit/zoom; X/Y/Z/W slice controls; wiring stage overlay; selected packet source/forward/inverse mapping; orthographic views; exploded toroid offsets; SVG engineering sheet, PNG view, Print-to-PDF, JSON scene save/load

## Frozen specification

```
{{{{ N184 :: BLUEPRINT REVISION B }}}}
60 rows × 40 columns = 2400 logical addresses
BOX    (2×2)^2  (4×4)^4  (6×6)^6
TOROID (1×1)^1  (3×3)^3  (6×6)^6
X  a(-2,+3) b(-3,+2) c(+2,-3) d(+3,-2)
{{**--``--**}}
ONE GATEWAY · v6.1 recovery frozen
```

## Reproducible verification

Open the [interactive lab](./) in a normal browser. Open developer console and check `N184 geometry check {vertices:16,edges:32,uniquePairs:38400}`. Rotate each 4D plane, change slicing axis/position, use the exploded view, route through 8 packet stages, and confirm source address and nibble are reconstructed. Exercise each export and load the JSON export again.

## Important limitations

- This is an **engineering visualization of a symbolic model**: geometry layers, toroid scales, and wiring flows are illustrative.
- Tesseract graph is exact; its 3D and screen projections may visually collapse edges in some views.
- X/Y/Z/W *slab filtering* operates on rendered edges (line-clipped), not true volumetric sliced faces or exact 4D polytope intersection geometry.
- "Exploded" shifts the toroid shells in the rendering; it is not a physically manufacturable assembly.
- Print/PDF uses browser print-to-PDF rather than a dedicated CAD PDF engine.
- The 60×40 address field is mathematically represented by the mapping and packet inspector. An individual 2400-cell in-scene lattice inset is not included in the main viewport.
- Source-file presence and structural checks were verified on GitHub, but interactive browser rendering and export behavior remain **unverified** in this environment.
- Frozen v6.1 acceptance tests are preserved as operator-reported evidence; do not infer new physical-force or quantum behavior.

## Source links

- [Prior Blueprint v6.2](../blueprint-3d-v62/)
- [Frozen v6.1 certification](../certification-v61/FREEZE.md)
