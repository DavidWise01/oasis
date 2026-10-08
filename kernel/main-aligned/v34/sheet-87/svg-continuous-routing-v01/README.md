# SHEET 87 — Native SVG continuous routing

Switch SHEET86 canvas view to **native inline SVG**. The finished standalone HTML (`index.html`) and static checks (`test_svg.py`) are available in the conversation ZIP `sheet87_svg_routing.zip`.

## Features

- Nine stable SVG -<>- portal diamonds, all 36 unordered portal connections represented by 120 uniquely identified lanes.
- Quadratic Bézier SVG `<path>` elements and SVG `<circle>` moving packets, no Canvas tag.
- Route offset changes at **portal arrival/departure only**, so position remains continuous across an existing curve and packet endpoint; steering angle need not be differentiable at the portal.
- Deterministic lane positions and IDs, live raw pairwise proximity count (<8 SVG viewbox pixels), looped completed lane traversals, pause/reset/speed toggles, experimental one-step route proposal, append-only in-browser ledger and downloadable ledger JSON.
- Earlier 60/15/3/1/1 six-arity grammar, 416 symbolic source registry and gravity phases retained in prior sheets; **this viewer does not execute physical gravity, delivery ACKs, or 9/6/1 scheduler**.

## Validation and limitations

14/14 static checks passed locally, including `svg` presence, absence of canvas, 120 lanes, Bézier geometry, per-frame pairwise distance measurement, unique IDs, identity ledger, UI controls and reset. **No interactive browser run or head-to-head runtime collision/delivery performance measurement has yet occurred**, so do not claim improved real-world safety or numerical performance. This is a visualization/interface upgrade, not an independent physical collision solution.

Executable HTML and static check source are available as downloadable files in the conversation. This repository entry is the append-only audit; previous sheets unchanged.
