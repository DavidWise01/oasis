# N184 Canvas2D production-path CPU benchmark — 2026-10-18

## Scope and provenance
Executed the currently committed `geometry.js`, `shared-scene.js`, `dirty-render.js` in a V8 JavaScript isolate using the renderer's four view angles. Each scenario: **600 simulated state evaluations × 3 trials**. Per dirty frame, computed four-viewport endpoint projections for each clipped segment; did not issue Canvas2D draw commands. Timings were recorded using integer-millisecond `Date.now()` and include no requestAnimationFrame wait.

| Scenario | Trial CPU times, ms | Median, ms | Median/frame, ms | Drawn | Skipped |
|---|---|---:|---:|---:|---:|
| Orbit | 4759, 4802, 4762 | 4762 | 7.94 | 600 | 0 |
| Idle | 11, 12, 11 | 11 | 0.0183 | 1 | 599 |
| Slice | 756, 757, 762 | 757 | 1.26 | 600 | 0 |

### Exact repeated output
- Orbit: 3,529 scene segments / drawn viewport; **2,117,400** segments per viewport accumulated across frames; four viewports projected.
- Idle: 3,529 scene segments / single draw.
- Slice: **169,434** clipped segments per viewport across 600 iterations (fewer segments due to clipping).
- Topology: **16 vertices, 32 edges, 38,400 reversible pairs**.

## Result and limitations
- **PASS:** geometry and mapping checks, dirty-frame idle skip of **599/600 = 99.83%**, deterministic projected coordinate checksum per scenario across three trials.
- **NO BROWSER FPS CERTIFICATION:** actual Canvas2D stroke calls, DOM overlays, GPU compositor, RAF schedule, picking, resize, exports, and sustained use not measured.
- This is a comparative source-level CPU preparation benchmark in the tool runtime, not results from the operator's actual Windows/Chrome GPU.
- Canvas2D remains selected as production renderer and WebGL2 experimental. Frozen v6.1 unchanged.
