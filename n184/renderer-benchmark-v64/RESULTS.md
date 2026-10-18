# N184 renderer benchmark — 2026-10-17

## Source-level measurements (executed)

Source: GitHub `blueprint-lab-v63/geometry.js`, `shared-scene.js`, `dirty-render.js`, executed as JavaScript in a V8 isolate. Five trials of 480 requests each.

| Metric | Recorded result |
|---|---:|
| Tesseract topology | 16 vertices / 32 edges |
| Address/nibble bijection | 38,400 / 38,400 |
| Full visual scene | 3,529 line segments |
| Uncached scene rebuilds, per 480 calls | [1146, 1114, 1101, 1102, 1078] ms |
| Uncached median | 1102 ms |
| Cached requests, per 480 calls | [4, 4, 4, 4, 4] ms |
| Cached median | 4 ms |
| Project 3,529 segment endpoints × 480 | [1016, 947, 937, 928, 941] ms |
| Projection median | 941 ms |
| Dirty-frame unchanged checks | 240 / 240 skipped |
| Camera-change redraw | PASS |

Caching avoids construction but **not** CPU endpoint projection, canvas stroke, or GPU submission. The ~99.6% change in cached-vs-uncached retrieval cost must not be described as an equivalent FPS gain.

## Comparative browser benchmark

Standalone harness: [Open N184 Canvas2D / WebGL2 comparison](./).

It runs Canvas2D and WebGL2 sequentially with the same 3,529 segment positions, 960×540 rendering target, changing camera angle, 3 trials each, and `gl.finish()` for command completion. CPU projection and buffer upload are included. Results must be captured in a real browser; **WebGL2 is not benchmarked in the assistant's source-only runtime**.

### Browser limitations

- Context initialization, memory allocation, shader compilation, canvas antialias options, and stroke-rasterization quality differ across backends.
- `gl.finish()` is a coarse synchronization point, not GPU timestamp-query profiling.
- This comparison uses plain lines rather than identical visual styling; it is a coarse throughput test, not a pixel-equivalent product benchmark.
- Run in foreground with browser devtools closed for reproducibility; repeat on the actual device. Report browser, GPU, and OS.

## Architecture decision

- **YES:** cached shared visual scene and dirty redraw are viable.
- **PENDING:** WebGL2 replacing Canvas2D; depends on observed browser timings and visual-quality parity.
- **FROZEN:** v6.1 kernel, mapping, transactional recovery and certificates.
