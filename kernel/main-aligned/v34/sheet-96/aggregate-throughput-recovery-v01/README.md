# SHEET 96 — D8 Aggregate Throughput Recovery (WASM + native SVG)

Append-only successor to SHEET95. The existing **single box** retains `8:0:8:0:8:0:8`, eight physical silo domains D0–D7, one nonphysical D8 aggregate, 72 toroid addresses (3 X + 3 Y + 3 Z² per floor), eleven symbolic copper sheets per floor, all 120 lane identities, and the 1.5-unit synthetic 3D via centerline-clearance guard. This upgrade **does not add a ninth physical floor** or change the D8 queue capacity of eight.

## Exact change

The SHEET95 bottleneck is an eight-tick, single-worker D8 FIFO, which can commit at most one handoff every eight ticks, however aggressively the upstream via paths are improved. SHEET96 adds an explicitly configurable *second logical service worker*. The first N (1 or 2) oldest admitted requests can each receive one tick of service per engine step. Each request **still requires eight full service ticks**. Both policies use identical admission (one per tick, source-silo round-robin with oldest-waiting-lane ordering), the same FIFO queue capacity 8, original four route choices and admission clearance rules, and the same five-tick synthetic destination ACK.

```
                    D8 logical aggregate
            ┌─────────────────────────────┐
  8 silos ──▶│ eight-slot shared FIFO      │
  D0...D7    │ [0][1][2][3][4][5][6][7]   │
            │  ╰─WORKER A─╯ 8 ticks each │
            │  ╰─WORKER B─╯ 8 ticks each │
            └─────────────┬───────────────┘
                          ▼
                   commit → receipt
                          ▼
                    five-tick ACK
```

Queue entries are granted service only from the FIFO head (or head+1) and committed in FIFO order. Completed transactions are counted by internal ACKs, **not acknowledgments from an external network**. A faster service worker **is a capacity change**, not an admission-only scheduling improvement.

## Reproducible compiled-WASM benchmark

Run actual WASM, seeded state, **2200 ticks per policy/scenario**. No mock engine. Validation requires per-tick conservation, 120 IDs, same eight-slot D8 queue, all 72 ring addresses, all eight domain sources serviced, swept-path clearance, immutable admitted paths, and deterministic reset/replay.

| Measure | Original 1-worker | New 2-worker |
|---|---:|---:|
| Normal modeled ACKs | 233 | **401** |
| Stress modeled ACKs | 271 | **449** |
| Normal upstream waiting, cumulative lane-ticks | 78,678 | **5,341** |
| Stress upstream waiting, cumulative lane-ticks | 103,463 | **26,409** |
| Stress clearance deferrals | **4,769** | 6,103 |
| Stress ACK count across initial 120 identities | 120/120 received >=1 | 120/120 received >=1 |
| Admitted 3D path-clearance violations | 0 | 0 |
| D8 capacity | 8 | 8 |

**48/48 executable WASM assertions passed**, including deterministic replay and every lane of the synchronized burst receiving an ACK. **74/74 SVG instrumented DOM checks passed** with the actual embedded WASM. A **real Chromium run passed**; 72 toroids, 88 copper traces, 120 packet markers, all eight FIFO slots, service-count switch, visible busy workers, and SVG route paths rendered without page errors. In a longer browser stress run there were 462 internal ACKs, one ACK pending, and no admitted clearance violation; browser timing means the final tick may vary.

**Important limitations:** D8 throughput improves because we doubled its logical workers; the higher throughput increases concurrent via requests and hence *clearance deferrals* (though admitted-path conflicts stay zero under this model). Completed service counts by source domain are unequal; round-robin admission and each initial lane being served do not establish equal steady-state fairness or worst-case wait bounds. There is no measured physical/electromagnetic PCB clearance, toroidal gravity, actual data-plane transport or external delivery confirmation. The append-only audit/ledger is in memory unless exported. All historical sheets (including failed improvement attempts) remain intact.

## Build and verification

```sh
clang --target=wasm32 -O2 -fno-builtin -nostdlib \
  -Wl,--no-entry -Wl,--export-all -Wl,--strip-all -o kernel.wasm kernel.c
python build_viewer.py
node test_wasm.js
node test_svg_dom.js
python test_browser.py  # Playwright + Chromium available
```

Open `index.html` directly as a local file. It contains the exact compiled WASM module embedded as base64, and does not fetch resources from a server. UI controls let you switch D8 between one and two workers, compare fixed/adaptive route shapes, run synchronized 120-lane stress, pause/reset, filter floors and axes, and export SVG/JSON event ledger. Export before reset to retain the session history.