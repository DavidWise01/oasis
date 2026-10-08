# SHEET 94 — 3D swept-path clearance, WASM and SVG

Append-only successor to SHEET93. The canonical parent topology is **8:0:8:0:8:0:8** (four eight-cell banks separated by three zeros), eight silo/domain floors D0–D7, one nonphysical aggregate D8, nine toroid addresses per silo (3 X + 3 Y + 3 Z²), eleven copper planes per silo (−5..+5, center `{{−1::0::+1}}`), 120 stable lane IDs and an eight-slot D8 FIFO.

## What changed from SHEET93
Before via admission, execute an **analytical nearest-distance test between the full two-segment 3D candidate via polyline and every presently admitted via polyline**. A lane stays at its source until the whole candidate route has ≥ **1.5 synthetic units** centerline separation from each admitted route. This is a conservative geometric reservation, not a time-synchronized moving-particle check. The 3D points are origin → midpoint → destination; an X midpoint bend creates real tests of crossings between different toroid IDs, which SHEET93 shared-anchor reservations could not detect.

Symbolic coordinates: `x=8×(ring mod 3)`, `y=8×floor(ring/3)`, `z=12×silo+0.3×(copper−5)`; midpoint x displacement = +3.6 (ring column 0), −3.6 (column 1) or 0 (column 2). An adversarial pair in neighboring ring columns has segment distance 0.8 and must be blocked. Geometry and distances are **arbitrary simulated units**, not physical PCB measurements. Each granted via takes 24 ticks; cross-floor transfers are serviced by D8 in 8 ticks; destination receipt then modeled ACK in 5 ticks. All events are deterministic and recorded in an exportable session ledger.

## Executed tests (same initial seeds, 2200 ticks)

| Metric | Normal | Stress 120 |
|---|---:|---:|
| Internal destination handoffs and modeled ACKs | 233 | 271 |
| All clearance deferrals | 2294 | 5934 |
| Cross-ring deferrals | 1271 | 2010 |
| Peak concurrent vias | 27 | 33 |
| Active full-route path violations | 0 | 0 |
| Aggregate FIFO occupancy at cutoff | 8 | 8 |

**37/37 actual compiled-WASM runtime checks passed**, including 120 identities, nine domain conservation, deterministic replay, ACK accounting, aggregate FIFO invariants, and adversarial cross-ring geometry. **64/64 instrumented SVG interface checks passed** against the actual embedded WASM. A **real Chromium run passed** without page errors; at tick 2274 under stress it had 280 modeled receipts and ACKs, no admitted swept conflicts, 5969 recorded clearance deferrals. Browser rendering displays 72 toroid groups, 88 copper traces, 120 packet markers, eight D8 queue slots and bent via SVG paths.

## Exact source, build and run
The downloadable artifact `sheet94_3d_swept_wasm_svg.zip` contains:
- `kernel.c` (freestanding C WASM model), `kernel.wasm` (compiled executable) and `index.html` (standalone SVG containing the real compiled WASM as base64).
- `rebuild.py`, `test_wasm.js`, `test_svg_dom.js`, `test_browser.py`.
- Full runtime and browser `results.json`, `summary.json`, README, Chromium screenshots, SHA256 manifest.

Rebuild using `clang --target=wasm32 -O2 -fno-builtin -nostdlib -Wl,--no-entry -Wl,--export-all -Wl,--strip-all -o kernel.wasm kernel.c`, then `python rebuild.py`, `node test_wasm.js`, `node test_svg_dom.js`, and `python test_browser.py` where Playwright/Chromium are installed.

Source SHA256: `6e3dedfedf8a1849e0274b345b38cb72d38af4cefba12d605b3c7b302f298d59`. Compiled WASM SHA256: `8a9f318cd07f15658e8efa848e2605b2d55b585262b5a995ae53ff57ec2f96ab`. Standalone HTML SHA256: `e92e8ff24fb6fff370579ed844c39ec5dc04a121d03cdf20417d1155335a95a5`.

**Limitations:** This is not fabrication clearance (PCB DRC), electromagnetic integrity, real gravity, a 3D solid-body swept-volume solver, or external network receipt verification. The simulated controller can increase clearance holds and backlog; its no-conflict outcome is conditional on the modeled immutable route paths and the chosen clearance limit. Historical kernel sheets remain intact.
