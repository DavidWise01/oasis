# N184 v6.7 — User browser benchmark evidence

**Browser-report timestamp:** 2026-10-18T04:41:44.935Z
**Recorded:** 2026-10-18
**Origin:** User-pasted JSON from the [unified benchmark](./).
**Status:** Operator-reported results; not independently run by the assistant.

## Exact performance readings

| Measurement | Result |
| --- | ---: |
| Geometry | 16 vertices, 32 edges |
| Reversible mappings | 38,400 |
| Scene segments | 3,529 |
| Renderer comparison frames | 90 |
| Canvas2D trial times (ms) | 24.3, 15.2, 13.4 |
| Canvas2D median (ms) | 15.2 |
| WebGL2 trial times (ms) | 8.8, 8.5, 6.8 |
| WebGL2 median (ms) | 8.5 |
| Canvas2D/WebGL2 duration ratio | 1.7882 |
| Reduction in comparison elapsed time | 44.08% |

### Full viewport scenarios

| Scenario | Drawn | Skipped | CPU median | CPU p95 | Elapsed |
| --- | ---: | ---: | ---: | ---: | ---: |
| Orbit | 180 | 0 | 0.2 ms | 0.5 ms | 1500 ms |
| Idle | 1 | 179 | 0 ms | 0.1 ms | 1499.7 ms |
| Slice | 180 | 0 | 0.2 ms | 0.8 ms | 1508.3 ms |

Reported cumulative scene-build counters: orbit 2, idle 3, slice 4; cumulative clipped-build counters: 2, 3, 183.

## Disposition

**WEBGL2 CANDIDATE — visual parity and long-run stability still required.**

WebGL2 is faster in this reported line-rendering comparison, but the tests use different rasterization paths and do not establish identical appearance or full-product FPS. Adopt as an optional rendering backend only after projection, picking, slicing, export, fallback and prolonged-operation equivalence checks. Keep Canvas2D default until then.

Frozen v6.1 mapping, geometry constants and recovery implementation are unchanged. No claim of physical mechanics, crash/power-loss durability or hardware certification.
