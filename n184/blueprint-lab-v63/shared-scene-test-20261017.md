# N184 shared-scene visual renderer — test record (2026-10-17)

**Scope:** rendering and wiring only. Frozen v6.1 mapping and persistence code unchanged.

## Commits in this chunk

- `shared-scene.js`: owned-snapshot geometry and clipped-segment caches.
- `app.js`: reuse one clipped scene for all four cameras; avoid repeated canvas dimension assignment.
- `index.html`: load shared-scene before application.

## Executed source-level tests

| Test | Result |
|---|---|
| Cached segments match original line-by-line (JSON representation) | PASS |
| Original vs shared scene segment count | 3,529 = 3,529 |
| Four sequential viewport requests from unchanged state | 1 geometry construction, 1 clip, 4 cache hits |
| Cache snapshot unaffected by later geometry generation | PASS |
| Rotation change invalidates geometry cache | PASS |
| Slice mode change recalculates clipped segments | PASS |
| X slab segment count (sample) | 458 |
| Tesseract topology | 16 vertices, 32 edges |
| Full inverse map | 38,400 reversible and unique |

All source-level results were computed from retrieved GitHub source in a JavaScript test isolate. These are **not live GitHub Pages browser FPS results**.

## Performance boundary

The shared geometry cache prevents repeating the expensive toroid reconstruction four times per display frame. Canvas2D still draws on a continuous animation loop; dirty-frame scheduling and WebGL2 remain separate future optimizations. Recheck live camera drag, slicing, vertex picking and engineering exports in a browser before certifying visual behavior.
