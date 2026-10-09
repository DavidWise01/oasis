# OaSIs SHEET 97 — Eight-Silo Fairness Governor (WASM / SVG)

Append-only successor to SHEET96. **One boXY box**: `8:0:8:0:8:0:8`, eight physical silo domains D0–D7, nine toroid addresses per silo (3 X, 3 Y, 3 Z²), eleven copper sheets per floor (L−5…L+5; `{{−1::0::+1}}`), one nonphysical D8 aggregate with exactly **eight** FIFO slots, **two** parallel eight-tick logical service workers, 120 immutable lane identities and synthetic five-tick destination ACKs.

```text
                       BOX :: ||||| /0\ |||||
                  8 - 0 - 8 - 0 - 8 - 0 - 8
    ┌─────────────────────────────────────────────────┐
    │ D0 D1 D2 D3 D4 D5 D6 D7     8 ISOLATED SILOS   │
    │ └─────────┬────────┘        9 TOROIDS EACH     │
    │           ▼               11 COPPER LAYERS    │
    │    WAITING REQUESTS                              │
    │           │                                      │
    │    ┌──────▼───────────────┐                     │
    │    │ D8 AGE + DEFICIT    │  RR BASELINE SWITCH │
    │    │ 96-TICK AGE TRIGGER │                     │
    │    └──────┬───────────────┘                     │
    │           ▼                                      │
    │     FIFO [0][1][2][3][4][5][6][7]              │
    │       WORKER A + WORKER B (8 TICKS EACH)        │
    │           │                                      │
    │     RECEIPT -> SYNTHETIC ACK                    │
    └─────────────────────────────────────────────────┘
```

## Exact causal change

The source-silo selection stage now offers policies via WebAssembly exports: `set_fairness_policy(0)` retains SHEET96 RR admission, `set_fairness_policy(1)` enables governor. Both retain original fair round-robin tie orientation, **at most one D8 admission per tick**, unchanged two D8 workers, eight total FIFO slots, FIFO commit order, geometry and ACK rules. For each eligible source domain, the governor considers its oldest waiting request and first prefers the domain with the fewest cumulative D8 admissions; ties prefer the older eligible request, then rotated source order. If any request has already waited **96 ticks or more**, the oldest such request is selected first. The override is *not* a guaranteed maximum waiting time: the D8 FIFO may be full, so the oldest request might still wait longer than 96 ticks. A granted 3D route never changes shape mid-via. Events remain append-only within the browser session until reset; export JSON before reset for durable preservation.

## Head-to-head actual compiled WASM, 2,200 ticks per scenario

| Metric | RR baseline | Age + deficit governor |
|---|---:|---:|
| Normal modeled ACKs | 401 | **403** |
| Normal upstream waiting (lane-ticks) | **5,341** | 5,370 |
| Normal clearance deferrals | **2,336** | 2,361 |
| Stress modeled ACKs | 449 | **457** |
| Stress upstream waiting (lane-ticks) | 26,409 | **23,523** |
| Stress maximum measured admission wait (ticks) | 385 | **377** |
| Stress clearance deferrals | 6,103 | **6,054** |
| Stress per-silo completed handoff spread (max − min) | **22** | 23 |
| Admitted swept-path violations | 0 | 0 |
| Lane ID conservation | 120/120 | 120/120 |

**The governor lowered cumulative upstream waiting by 2,886 lane-ticks (10.9%) under the synchronized stress condition** and yielded eight additional modeled ACKs (~1.8%). This is without adding any service worker. However, **the per-silo count spread got worse (22 → 23), so the governor has NOT demonstrated equal per-silo service**. Normal traffic also slightly worsened in waiting and deferrals. Preserve these negative findings; do not claim universal fairness improvement. Absolute service levels partly reflect different source-silo request production, not merely arbiter discrimination.

## Executed validation

- `node test_wasm.js`: the **real** compiled WebAssembly module passed **56/56 assertions**, including per-tick invariants for four policy/scenario combinations, zero admitted swept conflicts, exact D8 FIFO and nine-domain conservation, 120 identities, deterministic replay, immutable routes, and all 72 floor-ring addresses visited.
- `node test_svg_dom.js`: standalone HTML with the actual embedded WASM passed **81/81** instrumented-interface assertions (not browser paint), including eight source-scoreboard bars, switching policies, 72 rings, 88 copper traces, 120 markers and eight FIFO slots.
- `python test_browser.py`: headless Chromium rendered the standalone file and switched both policies with **zero page errors**. A longer stress snapshot reported 467 synthetic ACKs, 90 age overrides, zero admitted conflicts, and all eight D8 slots present. Render screenshots included.
- SHA256SUMS and ZIP CRC verified; HTML embeds the compiled WebAssembly module directly and runs offline. No HTTP request required.

## Reproduce

```bash
clang --target=wasm32 -O2 -fno-builtin -nostdlib \
  -Wl,--no-entry -Wl,--export-all -Wl,--strip-all \
  -o kernel.wasm kernel.c
python build_viewer.py
node test_wasm.js
node test_svg_dom.js
python test_browser.py  # requires Chromium and Playwright
```

Open `index.html`. The app exposes FIFO worker selection (one/two), fixed/adaptive geometry, RR/governor admission, synchronized stress 120, pause, reset, floor/axis filter, SVG export and JSON event export. The **head-to-head numerical comparison uses two workers for both policies**.

**Scope:** Synthetic centerline-separation constraint, abstract toroid geometry, symbolic copper layers and internally generated ACK events. No physical PCB clearance, electromagnetic verification, actual network delivery, real-world bounded fairness theorem, or live external connection is established. Earlier SHEETs are not overwritten.