# SHEET 92 — D8 Bounded Aggregate Arbitration · WASM / SVG

**Lineage:** append-only successor to SHEET 91 (`kernel/main-aligned/v34/sheet-91/eight-silo-one-aggregate-v01`). This is a new executable box, not a modification to historical sheets.

## Geometry

- One symbolic box `8 : 0 : 8 : 0 : 8 : 0 : 8`, eight physical silo floors/domains **D0…D7**, one **logical** aggregate **D8**.
- Nine toroids on each floor, three X, three Y, three Z². Total: **72 toroids**; the signed floor address is always retained so `z²` does not alias floors.
- Eleven copper sublayers L−5…L+5 per silo (88 symbolic traces); center register `{{−1::0::+1}}` remains the midpoint.
- 120 stable lane identities 0…119, four octet banks and three zero seams.

## Executable controller in freestanding WebAssembly

The compiler builds a real `wasm32` module from `kernel.c`; `build_html.py` embeds the exact module into native SVG `index.html`, so the viewer requires no external WASM fetch or network access.

A completed orbital lap performs a 24-tick copper or floor-via interpolation. Every third transfer is cross-floor. Cross-floor requests **wait at the target via anchor** until accepted by D8, while retaining their *original silo/domain identity*. A single causal arbiter observes only current/previous state, admits at most one candidate per tick and alternates between silos with a rotating round-robin cursor. Within a silo, selection is oldest waiting tick, then lowest lane ID as deterministic tie-breaker. Requests enter an **8-slot FIFO**; one FIFO head at a time receives eight service ticks. Only completed service commits the target floor and target domain. All other requests wait; **nothing is dropped**. In the SVG, waiting markers are red, admitted D8 residents are gold, and the FIFO displays actual lane IDs in eight slots.

Conservation laws checked on **every simulated tick**:

```
aggregate admissions == committed handoffs + queue occupancy
aggregate occupancy <= 8
aggregate occupancy == count(lane.phase == D8_QUEUE)
waiting outside == count(lane.phase == WAIT)
D8 population == aggregate occupancy
sum(entries(domain) - exits(domain), D0..D8) == 120
floor transfers == aggregate commits
```

**Stress 120** synchronizes initial lane completion so all 120 requests reach the vertical-via boundary at once, creating authentic queue saturation/backpressure; once those first requests complete, normal ongoing orbital traffic may keep the FIFO busy. It is wrong to require the queue to be empty at a fixed late tick.

## Verification

- Actual compiled WASM running in Node: **27/27 assertions**, plus per-lane state and domain-conservation checks on every tick, across the normal and synchronized-stress 1,800-tick experiments and exact deterministic replays.
- Initial stress burst: every one of 120 original lanes completed its first transfer (minimum hop count ≥3). At tick 1,800: 229 aggregate admissions, 221 commits, 8 queued, 43 waiting; maximum waiting 119; FIFO reaches capacity 8; 1,769 full-queue pressure ticks. Eight silos received 27–28 commits each in this scenario. **This does not guarantee bounded wait under every future arrival pattern.**
- Embedded-WASM SVG JavaScript executed in instrumented DOM: **52/52** checks across 600 animation frames / 1,200 WASM ticks, including stress/reset/pause/selection and ledger.
- Actual Chromium browser render via Playwright: **PASS** — 72 SVG toroid groups, 8 queue rectangles, 120 packet markers, successfully engaged stress with queue 8 / waiting 108, and no page errors. Because direct local `file://` navigation was blocked by browser policy, the test loaded the exact standalone HTML via `page.set_content`. Its HTML and inline executable were the same.
- `node --check` / inline JS parsing, ZIP CRC and SHA-256 integrity manifest are validated before distribution.

## Run

Open `index.html` in any current browser with WebAssembly enabled, or use `python -m http.server` from this folder. Buttons: pause/resume, normal reset, **Stress 120**, speed, floor and axis filters, SVG export, JSON append-only session ledger export. The reset button starts a fresh local session; export the ledger first if persistence is needed.

Recompile: `clang --target=wasm32 -O2 -fno-builtin -nostdlib -Wl,--no-entry -Wl,--export-all -Wl,--strip-all -o kernel.wasm kernel.c`, then `python build_html.py`. Test: `node test_wasm.js`, `node test_svg_dom.js`, `python test_browser.py` (requires Playwright + Chromium).

## Boundaries

The system simulates symbolic domain arbitration and SVG toroid projections. Queue admission and backpressure are real runnable WASM logic, but **not** physical electrical conductance, gravitational forces, manufacturing PCB design-rule checks, continuous 3D collision clearance or actual acknowledged packet delivery. Aggregate is a logical ninth domain, **not** a ninth floor. Fairness measurements are empirical and specific to the evaluated workloads, not a proven worst-case fairness or hard deadline guarantee.