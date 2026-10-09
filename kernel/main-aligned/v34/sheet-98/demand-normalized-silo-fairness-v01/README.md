# OaSIs SHEET 98 — Demand-Normalized Eight-Silo Fairness (WASM + native SVG)

Append-only successor to SHEET97, using its exact freestanding C / WASM eight-silo model and real native SVG viewer as the source. Retains **8:0:8:0:8:0:8**, 8 physical silos D0..D7, 9 symbolic toroids each (3 X, 3 Y, 3 Z²), 11 copper sublayers each L−5..L+5 with `{{−1::0::+1}}` center rail, 120 unique lane identities, and one logical D8 aggregate (8-slot FIFO, two 8-tick workers). The clearance guard is a 1.5-unit minimum distance between pairs of *complete 3D two-segment route polylines*; this is not physical PCB clearance. Receipts and ACKs remain **modeled internal events**, not external data-plane delivery confirmations.

## New instrumentation and policy

An **eligible request** is created only when a completed 24-tick via from a physical silo reaches the D8 admission waiting state. This does not count unmaterialized demand or simulated orbit events. Each silo tracks `eligible`, `admitted`, `pending = eligible - admitted`, `modeled ACK`, cumulative upstream waiting lane-ticks, p95 and worst-case admission wait among admitted items. Histograms are discrete integer ticks (4096 buckets, clamping beyond 4095). A single live normalized share is `admitted / eligible` (displayed in basis points) and live Jain score applies to eight such shares. Interpret cautiously: when all outstanding requests are admitted, all eight ratios reach 1.000, even though actual waits can differ sharply. Inspect intermediate burst timestamps and waiting quantiles.

Policies selectable within the same compiled binary:

0. **SHEET96 source round-robin** baseline, oldest within each source.
1. **SHEET97 age + historical issued deficit**, age override at 96 ticks.
2. **SHEET98 demand-normalized**, lowest admitted/eligible ratio across currently waiting sources. Compare ratios exactly using integer cross-products (no approximate floating-point ordering); tie-break by oldest waiting request then source rotation. Retain global oldest-first 96-tick age override. Admitted routes are immutable; no extra D8 workers or queue slots.

The interactive standalone HTML embeds the real compiled `kernel.wasm` as base64, paints toroid routing in native SVG and includes the D0..D7 demand/ACK/p95 dashboard, per-domain normalized bars, Jain snapshot, policy selector, normal and simultaneous 120-lane stress buttons, an intentionally skewed demand workload, filters, speed controls, pause/reset, SVG export, and a per-session append-only event ledger. Export the ledger before session reset; no persistent remote ledger is implied.

## Actual compiled-WASM verification — three matched workloads

Same deterministic initialization, 2200 ticks, 2 service workers, 8 D8 slots, 120 lanes and adaptive via-routing geometry across policy comparisons. **76/76 WASM runtime checks** passed. Every tick verifies bounded queue, 9-domain/120-lane population, full-path clearance, immutable granted paths, ACK/receipt accounting, and source-level eligible−admitted=pending and waiting-lane-ticks sum. Replay is deterministic.

| Metric | SHEET97 age/deficit | SHEET98 normalized |
|---|---:|---:|
| Normal ACKs | 403 | 403 |
| Normal cumulative upstream waiting | 5,370 | 5,378 |
| Normal worst silo p95 admitted wait | 77 | 75 |
| Burst ACKs | 457 | **456** |
| Burst cumulative upstream waiting | 23,523 | **23,254** |
| Burst full-route clearance deferrals | **6,054** | 6,287 |
| Burst worst silo p95 admitted wait | 345 | 345 |
| Uneven-demand ACKs | 448 | **449** |
| Uneven-demand full-route clearance deferrals | 4,815 | **4,627** |
| Uneven-demand cumulative waiting | **7,443** | 7,450 |
| Admitted full-route clearance violations (all runs) | 0 | 0 |

The synchronized burst has 15 eligible lanes per physical silo. The intentionally skewed stress has 15 immediate candidates each in D0–D3 and 3 immediate candidates each in D4–D7 (other lanes continue normally). At 2200 ticks all eligible requests happen to be admitted in these runs, so **the final per-silo normalized admission score is identically 100% and cannot validate fairness by itself**. The viewer exposes transient ratios and latency tails to prevent this false conclusion.

**Interpretation:** This is a genuinely implemented *fairness accounting and scheduler comparison*, not a universally better algorithm. Its burst cumulative waiting improves by only 269 lane-ticks (about 1.1%), with one fewer modeled ACK and more clearance deferrals. Under uneven demand, ACK count rises by one and deferrals fall, but total waiting rises slightly. The age-first criterion limits how often the ratio changes selection during prolonged overload; no unconditional fairness or latency guarantee has been established.

## Tests and browser

- `node test_wasm.js` — actual compiled binary; **76/76 checks** including time-window fairness snapshots, normal, synchronized and uneven-demand loads.
- `node test_svg_dom.js` — embedded WASM and real viewer JS against a structured DOM instrument; **89/89 checks** and 600 animation frames. The DOM test is not a browser paint test.
- `python test_browser.py` — **actual Chromium** rendered and interacted with the standalone viewer using Playwright content injection (local `file://` navigation was blocked by the harness). **19 assertions**, zero page errors; it confirmed 72 toroids, 88 copper traces, 120 lane markers, eight D8 queue slots, visible Jain/p95 data and the 15/3 skew. Screenshots `viewer_stress.png`, `viewer_skew.png`, `viewer.png`.
- `clang --target=wasm32 -O2 -fno-builtin -nostdlib -Wl,--no-entry -Wl,--export-all -Wl,--strip-all -o kernel.wasm kernel.c` compiles a freestanding module; `python build_viewer.py` reconstructs the exact embedded viewer **using the included `base_sheet97.html`**. No external site is needed to open the finished viewer.
- `SHA256SUMS.txt` records exact package-file hashes; ZIP CRC is checked before delivery.

Limitations: no real PCB design-rule check, electromagnetic integrity, gravitational simulation, physical network transport, or external ACK verification; the 3D centerline model is illustrative and its constant is in synthetic units. The aggregate's eight-slot bound does not imply the upstream waiting area is capacity bounded. Earlier SHEET97 implementation and negative benchmark findings are left unmodified.