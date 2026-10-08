# SHEET 91 — Eight Silos / Eight Domains / One Aggregate

`8 0 8 0 8 0 8` forms one box. Each of its eight logical floors is a silo and is an isolated domain **D0–D7**. The **+1 aggregate** is **D8**, a control/transfer domain, not an additional physical floor or another nine rings. Each silo keeps **9 toroid addresses = 3 X + 3 Y + 3 Z²**, **11 symbolic copper sublayers L−5…L+5** and center `{{−1::0::+1}}`. The whole box therefore contains **72 toroids, 88 copper sublayers and nine logical address spaces** (8 domains + 1 aggregate). The existing four banks and three zero seams `8:0:8:0:8:0:8` remain as in SHEET90. All 120 lane IDs remain unique, and no identity is discarded or duplicated.

## Executable WASM model

The real freestanding `kernel.wasm` is compiled from `kernel.c` using `clang --target=wasm32`, then embedded as base64 in the standalone, local-file-friendly `index.html`. The browser uses native SVG for visualization. The inner kernel is an abstract state machine, not an electrical PCB simulator.

Every third completed orbit initiates an inter-floor transfer, with **24 ticks** of interpolated vertical-via motion and then **8 ticks** in the logical D8 aggregate for admission to the destination domain. Copper-only transfers use the 24-tick via but do not enter the aggregate. The lane's physical floor value changes **only** after the aggregate commit. The aggregate is rendered as an activity strip and pending lanes are highlighted at the destination anchor. Its address is `8` while physical floors are strictly `0..7`. At any tick:

- `aggregate_ingress == aggregate_commits + aggregate_pending`
- `floor_transfers == aggregate_commits`
- `sum(domain_entries[d] - domain_exits[d] for d=0..8) == 120`
- `domain_id == 8` iff the lane is in aggregate commit phase.

The session UI offers pause, reset, speed, floor/axis filter, export SVG and export of an append-only in-memory event ledger. Export the ledger before reset; reset intentionally starts a fresh session. This is not permanent remote storage.

## Tests and measured result

`node test_wasm.js`: actual compiled WASM exercised **1,800 ticks, 38/38 assertions** plus per-lane/per-tick invariant checks. Results: **1,164 orbit completions**, **1,147 fully completed vias**, **343 committed cross-floor handoffs**, **344 aggregate admissions**, **1 pending aggregate item** at cutoff, **all 72 floor/toroid addresses visited**; reset and replay byte-equivalent end states. All 9 logical domains observed.

`node test_svg_dom.js`: actual standalone HTML's embedded WASM exercised under an instrumented DOM over **600 animation frames / 1,200 WASM ticks**, **40/40 checks**. SVG structure includes 8 visible physical silo bands, 72 toroid groups, 88 copper trace lines, 120 lane circles and D8 aggregate activity. The test is **not a graphical browser paint test**. Inline JavaScript parsed successfully and the package ZIP passed CRC test.

The domains are **logical, not electrically isolated in a fabricated motherboard**. No real electrical routing isolation/DRC or via clearance has been simulated. No packet arrival acknowledgments, network throughput, gravitational force or 9/6/1 priority scheduler are implied. Toroids are symbolic SVG ellipses, not 3D copper windings. Z² is a display coordinate and each domain/floor retains a unique signed ID (do not collapse mirrored floors). The aggregate is a deterministic, unbounded logical commit stage without congestion back-pressure or arbitration yet; those require separate benchmarks.

## Build and reproducibility

```sh
clang --target=wasm32 -O2 -fno-builtin -nostdlib -Wl,--no-entry -Wl,--export-all -Wl,--strip-all -o kernel.wasm kernel.c
python3 build_html.py
node test_wasm.js
node test_svg_dom.js
```

The compiled binary is separately usable, and `index.html` embeds it so it opens without a web server. Package includes `kernel.c`, `kernel.wasm`, `build_html.py`, `index.html`, `test_wasm.js`, `test_svg_dom.js`, `results.json`, `README.md`, and a SHA-256 manifest. Previous OaSIs sheets remain unchanged; SHEET91 is append-only.