# N184 v6.8 user browser certification report

Operator-reported timestamp: **2026-10-18T06:18:24.151Z**.
Source: user-pasted result, not independently browser-verified by assistant.

## Geometry
- vertices: 16; edges: 32; unique reversible pairs: 38,400.

## Parity
- Pixel count: 256,000.
- Difference above intensity threshold 25: 5.2% of pixels.
- Mean channel intensity error: 3.34.
- Lit pixels: Canvas2D 18,166; WebGL2 13,769.
- Lit pixel IoU: 0.758.
- **Disposition:** parity not established; compare line thickness, anti-aliasing and marker/annotation consistency.

## Stress
- 1,800 draws in 492.9 ms (not 30 seconds).
- Median CPU + synchronized GPU time: 0.1 ms; p95: 0.3 ms.
- Context lost during stress: false.
- **Disposition:** short stress pass, sustained performance not established.

## Recovery
- Original result: `recoveryError: "Error: null"`.
- **Disposition:** not passed; do not classify this as a GPU failure.
- Harness updated in commit `38b7b1667cae664bec4ce1689f300c2587ce85e6`: wait for `webglcontextlost` and `webglcontextrestored`, prevent default context-loss behavior, then reinitialize resources and redraw; errors now have useful text.
- **Re-run context recovery in browser before switching default.**

Decision: WebGL2 remains **optional**, Canvas2D default and fallback. Frozen v6.1 unaffected.
