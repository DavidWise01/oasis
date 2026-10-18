# N184 v6.5 three-scenario execution — 2026-10-17

## Execution environment and scope

Executed the committed `blueprint-lab-v63/geometry.js`, `shared-scene.js` and `dirty-render.js` in a V8 JavaScript tool isolate. Recreated v6.5 orbit/idle/slice state changes for 180 iterations each, projected every segment endpoint for frames marked dirty. Did **not** execute browser Canvas2D strokes or WebGL2 commands. Chromium navigation was blocked by the administrator, including for a local page. Consequently **no FPS, RAF interval, or canvas raster time is established**.

## Results

| Metric | Camera orbit | Idle | Slice |
| --- | ---: | ---: | ---: |
| Iterations | 180 | 180 | 180 |
| Frames marked for redraw | 180 | 1 | 180 |
| Skipped | 0 | 179 | 0 |
| Segments whose endpoints were projected | 635,220 | 3,529 | 50,645 |
| CPU loop wall time | 362 ms | 6 ms | 158 ms |
| Median millisecond-resolution preparation time | 2 ms | 0 ms | 1 ms |
| 95th-percentile millisecond-resolution preparation time | 2 ms | 0 ms | 1 ms |

The 0 ms value reflects the integer-millisecond wall-clock resolution, not zero CPU work. Timings are one pass, not statistical performance claims; system load and JIT warmup were uncontrolled.

### What the tests demonstrate

- Orbit invalidates the dirty-frame signature on each camera change while shared geometry is reused.
- Idle skips 179 of 180 unmodified frames (99.4%).
- Slice position changes trigger recalculation of clipped segments, but not regeneration of underlying toroid and tesseract geometry.
- Source-level topology and mapping still check: 16 vertices / 32 edges / 38,400 reversible address-and-nibble states.

### What remains unverified

The actual benchmark at [v6.5](./) must still run in an ordinary browser to measure Canvas2D, frame intervals and user-device behavior. Comparing Canvas2D vs WebGL2 still requires the [v6.4 browser test](../renderer-benchmark-v64/). Do not conclude 60 FPS or recommend a GPU backend from these CPU preparation values alone. Frozen v6.1 mapping and recovery unchanged.
