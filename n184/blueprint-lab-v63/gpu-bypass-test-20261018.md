# N184 optional GPU bypass verification — 2026-10-18

**Scope:** visual renderer selection only. Frozen v6.1 kernel, mapping and recovery are unchanged.

The `app.js` render path now uses:
- Canvas2D for the main viewport in default mode.
- Only WebGL2 for the main viewport if the experimental backend is selected and draws successfully.
- Immediate Canvas2D redraw if the GPU draw call reports failure.
- Three orthographic views remain Canvas2D, with drafting and export paths unchanged.

## Executed source-level branch tests

| Condition | Expected | Observed |
|---|---|---|
| No GPU module | Canvas2D draw | PASS; one Canvas2D draw |
| WebGL2 enabled and successful | GPU draw; no Canvas2D | PASS; one GPU draw and zero Canvas2D |
| GPU draw returns failure | Canvas2D fallback | PASS; one GPU attempt and one Canvas2D draw |
| Manual Canvas2D selection | Canvas2D only | PASS; one Canvas2D draw |

Updated `app.js` parsed successfully after GitHub round-trip.

**Validation boundary:** conditional dispatch was tested with mock backend states. No live browser WebGL2 pixel-parity, context-loss recovery, memory usage, or sustained FPS benchmark has yet been executed for the integrated viewer. Keep Canvas2D default until those gates pass.
