# N184 Renderer Feasibility — 2026-10-17

**Decision:** Feasible to consolidate into one cached 4D→3D scene and four camera views. Implement as visualization-only; v6.1 recovery subsystem remains frozen.

## Reproducible source-level microbenchmark

Source: existing `geometry.js` loaded into a JavaScript V8 execution isolate. Complete default scene with tesseract, nested frames, three toroids, X-core, gateway and wiring, expanded 4D projection.

| Operation | Measurement |
| --- | ---: |
| Exact tesseract | 16 vertices, 32 edges |
| Exhaustive reversible mapping | 38,400 unique, reversible pairs |
| Segments in one complete scene | 3,529 |
| Original: 240 independent scene constructions | 495 ms |
| Proposed: 60 scene constructions, reused across four views | 118 ms |
| Reduction in geometry construction time | 76.2% |
| Non-finite geometry endpoints | 0 |

These runs compare different *geometry-construction counts* with an equivalent four-view rendering plan. They do not draw canvas frames or measure GPU behavior. Treat the number as a microbenchmark, not as a browser FPS gain. Repeated timing samples and a real-browser benchmark are required for performance claims.

## Architecture alignment

```text
ONE IMMUTABLE MODEL STATE
        |
  DIRTY-STATE CHECK
        |
  CACHED SCENE BUILD (once per change)
        |
  4D TRANSFORM (16 vertices / 32 edges)
        |
  SHARED SEGMENT BUFFER
        |
  +----+----+----+----+
  ISO FRONT TOP SIDE
        |
  CANVAS2D FALLBACK / WEBGL2 OPTIONAL
        |
  TECHNICAL DRAWING / MEASUREMENTS / WIRING
```

Proposed separation:

1. Cache toroidal mesh vertices and edge indices per geometric resolution and radius.
2. Recompute 4D projection only when rotation/projection changes.
3. Rebuild visual segment buffer only when geometry, visibility, explosion or slicing changes.
4. Camera movement changes only camera transforms, not 4D/3D geometry.
5. Render dirty viewports on demand; pause when page is hidden.
6. Retain Canvas2D as fallback if WebGL2 unavailable, and add comparative browser benchmarks before selecting GPU renderer.

## Cautions and test gates

- Existing `makeScene` returns a **mutable shared array**. A caching refactor must prevent aliasing between frames, measurements and slice operations (immutable snapshot or owned typed-array buffers).
- Tests needed: exact topology and 38,400 state mapping unchanged; all four views match existing coordinates; X/Y/Z/W slice intersections; vertex picking; export equivalence; no crash for unsupported WebGL2; real browser CPU/frame-time and GPU tests.
- The visual toroid counts are geometric mesh counts, **not physical simulation**.
- Existing renderer redraws continuously. This is the primary optimization target.
- No production performance or physical behavior is certified by this study.

**Status:** feasibility benchmark PASS for de-duplicating scene generation; WebGL2 and final 60 FPS target remain unverified.
