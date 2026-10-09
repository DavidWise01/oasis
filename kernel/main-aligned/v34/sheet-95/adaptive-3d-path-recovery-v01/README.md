# OaSIs SHEET 95 — Adaptive 3D Path Recovery (WASM + native SVG)

**Append-only successor to SHEET94.** One box `8:0:8:0:8:0:8` with eight isolated silo/floor domains D0–D7, logical eight-slot aggregate D8, nine toroids per floor (3 X / 3 Y / 3 Z²), eleven copper subplanes L−5..+5 per silo, and 120 uniquely retained lane identities. This is a deterministic **symbolic routing simulation**, not PCB fabrication, Maxwell electromagnetism, gravitational dynamics or external networking.

## Upgrade

SHEET94 always retried its original 3D via route; SHEET95 introduces a causal, bounded recovery proposal only at the **held** preadmission stage. It retains each route's source and destination and requires whole-path separation of ≥ **1.5 synthetic 3D units** from every already admitted via. A via's selected path is frozen until its transfer completes (24 ticks).

Proposals in priority order: (0) original ring-column inward bend, (1) straight midpoint, (2) bounded 3.6-unit lateral Y detour, (3) bounded 3.6-unit outward X detour. The controller evaluates only existing active reservations, up to four proposals per held tick, then either grants one safe path or holds the packet for later retry. Some modes duplicate in the third ring column; the limit is four proposals, not four unique paths at every address. The selected route is rendered cyan-green for alternatives or gold for the fixed default. These are bent two-segment centerlines; they are **not** swept solid geometries or a collision-free electrical PCB guarantee.

Control selector in `index.html`: **Adaptive (4 paths)** vs **Fixed baseline**. Switching resets the simulated session. All requests from floor crossings still pass through D8's source-silo round robin and eight-slot FIFO, and modeled ACKs occur five ticks after the D8 service completes. Ledger records each accepted mode and synthetic acknowledgment. Export the ledger before resets.

## Full architecture

```text
  8 : 0 : 8 : 0 : 8 : 0 : 8       ONE BOX
                  |
          +-----------------+
          | D8 = 8-slot FIFO|
          +-----------------+
                  |
         D7 [ X X X Y Y Y Z² Z² Z² ]  ||||| /0\ |||||
         D6 [ X X X Y Y Y Z² Z² Z² ]  ||||| /0\ |||||
         D5 [ X X X Y Y Y Z² Z² Z² ]  ||||| /0\ |||||
         D4 [ X X X Y Y Y Z² Z² Z² ]  ||||| /0\ |||||
         D3 [ X X X Y Y Y Z² Z² Z² ]  ||||| /0\ |||||
         D2 [ X X X Y Y Y Z² Z² Z² ]  ||||| /0\ |||||
         D1 [ X X X Y Y Y Z² Z² Z² ]  ||||| /0\ |||||
         D0 [ X X X Y Y Y Z² Z² Z² ]  ||||| /0\ |||||
                  |
        HELD via -> try fixed bend
                  | blocked
                  +--> straight -> Y detour -> X detour
                                      |
                               full-3D clearance
                                /            \
                             GRANT          HOLD
                                |             |
                          24-tick via       RETRY
                                |
                          D8 round robin
                                |
                         destination receipt
                                |
                       modeled five-tick ACK
```

## Verified actual WASM benchmark — matched workloads, 2,200 ticks per policy

| Metric | Normal fixed | Normal adaptive | Stress fixed | Stress adaptive |
|---|---:|---:|---:|---:|
| Clearance deferrals | 2,294 | **974** | 5,934 | **4,769** |
| Clearance-hold ticks | 3,224 | **1,906** | 6,730 | **5,564** |
| Completed vias | 866 | 869 | 741 | 742 |
| D8 committed handoffs | 233 | 233 | 271 | 271 |
| Modeled delivery ACKs | 233 | 233 | 271 | 271 |
| Alternative path grants | 0 | 81 | 0 | 74 |
| Active admitted-path violations | 0 | 0 | 0 | 0 |
| Waiting outside D8 at cutoff | 45 | 42 | 39 | 35 |

**WASM: 48/48 actual runtime checks passed**, including per-tick lane bounds, phase identity, immutable via route mode, D8 and ACK conservation, zero accepted-route conflicts, normal and synchronized-stress comparisons, and deterministic replay. **SVG: 70/70 instrumented DOM checks passed** for the embedded real WASM, topology, filters, adaptive route coloring, counters, and policy toggle. **Chromium: passed**, rendered all 72 rings / 88 copper traces / 120 dots / 8 FIFO slots and stress counters, with no page errors. Extended browser stress run recorded 278 modeled receipts and 278 ACKs, 74 fallback grants, and zero accepted path conflicts.

**Honest outcome:** candidate rerouting reduces clearance waiting but **does not improve D8 delivery throughput**, which remains the limiting eight-slot serial aggregate in this test. Measured route-length accumulation may differ from the fixed baseline because traffic histories diverge; the model gives every via 24 ticks regardless of path length, so it does not prove identical traversal velocity or bounded acceleration. The controller is causal and the experiment uses identical initial seeds for fixed/adaptive comparisons.

## Reproduce

```sh
clang --target=wasm32 -O2 -fno-builtin -nostdlib \
  -Wl,--no-entry -Wl,--export-all -Wl,--strip-all -o kernel.wasm kernel.c
python3 rebuild.py
node test_wasm.js
node test_svg_dom.js
python3 test_browser.py  # requires Playwright Python and Chromium
```

The viewer's `index.html` embeds the executable WASM data and can open directly as a local file. Source and binary are included separately. SHA-256 manifests are in `SHA256SUMS.txt`. The C source, tests, README, JS viewer, and results are append-only GitHub assets. Earlier sheets remain unchanged.