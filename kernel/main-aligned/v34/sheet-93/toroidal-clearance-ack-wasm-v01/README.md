# SHEET 93 — Toroidal Clearance + Modeled Delivery ACK

**Parent:** SHEET92 `kernel/main-aligned/v34/sheet-92/bounded-aggregate-wasm-svg-v01/`. This is an append-only executable successor. The original 8×9 toroid symbolic box remains `8:0:8:0:8:0:8`: D0…D7 eight physical silos, D8 one logical aggregate, 72 ring addresses, 88 copper mini-planes (11 per silo), a center `{{-1::0::+1}}` bus, 120 stable lane IDs, and eight FIFO slots with deterministic round-robin admission.

## Executed finite-state phases

```text
0 ORBIT
  └─►4 CLEARANCE HOLD (source via anchor)
          └─►1 GRANTED VIA (24 simulated ticks)
                ├─►0 COPPER TRANSFER COMPLETED
                └─►3 D8 WAIT (source domain remains owner)
                      └─►2 D8 QUEUED (8 slots, 8 service ticks/head)
                            └─►5 DESTINATION RECEIPT / ACK PENDING
                                  └─►0 ACK RECEIVED (5 simulated ticks later)
```

**Conservative logical spatial clearance rule:** each toroid has one logical radial via anchor per floor. Copper transitions reserve `(source_floor, ring)` while a cross-floor via reserves both `(source_floor,ring)` and `(target_floor,ring)`. An overlapping active reservation is held at its source anchor until that track is free. The check uses deterministic logical coordinates and doesn't pretend to solve 3D swept-solid clearance, self-clearance, electrical impedance, PCB fabrication DRC, or actual EM physics. Holding a via reservation does not drop lane identity. The shared aggregate remains physically separate from the 8 floors.

**Modeled ACK:** when the D8 FIFO commits a cross-floor handoff, increment `delivery_seq[lane]` and move the lane into ACK_PENDING for 5 ticks. When the timer expires, increment `ack_seq[lane]` and return the lane to ORBIT. Guarantees from the executable:

- `deliveries = aggregate_out = floor_vias`
- `deliveries = ACKs + ack_pending`
- For each lane: `0 ≤ delivery_seq[lane] - ack_seq[lane] ≤ 1`
- `aggregate_in = aggregate_out + aggregate_queue`; queue ≤ 8
- `sum(domain_entries[d] - domain_exits[d], d=0..8) = 120`
- No simultaneous via occupants share the same toroid/floor reserved track under the explicit reservation model.

The ACK is **a synthetic internal receipt**, not a real receiving endpoint or externally verified round-trip transport. ACK_PENDING is counted separately from service completion. The UI's ledger records clearance requests/grants, D8 admissions, destination receipts and ACK receipts. Export before resetting if permanent local retention is desired.

## Executed tests

- **Actual compiled WASM** `node test_wasm.js`: **29/29**, including per-lane and conservation checks every tick over **2,200 normal + 2,200 synchronized-stress ticks**, replay, six distinct runtime phases and identity conservation. Normal: 233 delivery receipts, 233 ACKs, 1,581 clearance deferrals; stress: 271 receipts, 271 ACKs, 5,007 clearance deferrals, 36 peak concurrent granted vias; **0 logical track conflicts**.
- **SVG integration** `node test_svg_dom.js`: **60/60 instrumented DOM checks**, 600 frames = 1,200 actual WASM ticks, including clearance/ACK counter checks, 72 rendered toroids, 88 symbolic traces, 120 moving packets, and 8 FIFO slots. This isn't a real browser paint test.
- **Chromium/Playwright** `python test_browser.py`: PASS. Screenshot captured for normal and stress states; 72 rings, 8 queue slots, 120 lanes, zero page errors. After direct WASM advancement in real Chromium at tick 2,274: **280 delivered, 280 ACKs, 0 track conflicts, 5,081 clearance deferrals**.
- `node --check` of inline JavaScript, archive CRC integrity, and SHA256 manifest checked.

## Rebuild and run

`clang --target=wasm32 -O2 -fno-builtin -nostdlib -Wl,--no-entry -Wl,--export-all -Wl,--strip-all -o kernel.wasm kernel.c`

`python build_html.py` (uses `source92.html` as the original SVG canvas and embeds the new compiled `kernel.wasm` into `index.html`).

`node test_wasm.js && node test_svg_dom.js && python test_browser.py`

Open `index.html` directly in a modern browser. The viewer is standalone with embedded WebAssembly and no external imports. `source92.html` is included for source/build reproducibility; the original SHEET92 GitHub artifact is not modified.

## Limits

This models routing and queueing in a discrete symbolic substrate. No electrical conduction, gravity field, physically valid fluid/toroid geometry, true continuous 3D swept volumes, external ACK endpoints, authenticated network packets, or real-world network delivery is demonstrated. Round-robin fairness observed for this test does not prove worst-case service bounds for arbitrary workloads. No previous sheet is deleted or overwritten.