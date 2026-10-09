# OaSIs SHEET 99 — Per-Silo Latency Audit + Deadline-First D8 (WASM/SVG)

Append-only successor to SHEET98 in `kernel/main-aligned/v34`. The canonical physical topology remains **one box `8:0:8:0:8:0:8`**, eight independently addressable silo domains D0–D7, nine toroid addresses per silo (three X + three Y + three Z²), eleven copper sublayers per silo (`||||| /0\ |||||`), the center `{{−1::0::+1}}`, 120 lanes with persistent IDs, and one **logical**, not physical, D8 aggregate. D8 maintains an eight-slot bound and **two** independent eight-tick service workers; only the *admission policy* changes. Synthetic 3D clearance for all proposed via polylines is unchanged (centerline spacing 1.5 simulation units). Modeled destination receipts/ACKs and append-only session ledger remain intact.

## Added scheduler

Policy `3` selects the **earliest-arriving eligible D8 waiting request globally** (`arrival_tick` ascending, then lane ID). This implements a directly testable *no-overtaking ordering rule*. An SLA target of 96 ticks flags late admissions (`get_sla_overdue`) and current waiting lanes older than the target (`get_overdue_pending`). **96 ticks is a soft scheduling objective, NOT a hard latency guarantee:** bounded aggregate throughput, via clearance holds, and ongoing arrivals can force lateness. A proof of bounded worst-case delay would require external arrival-rate/envelope assumptions; none are established here. The 96-tick target measures *D8 eligibility → admission* only, not earlier via wait, D8 processing, or external delivery.

The old SHEET97 least-issued+age and SHEET98 demand-normalized+age schedulers remain switchable as policies 1 and 2. Round-robin policy 0 also remains. A policy switch resets only the in-memory session; export the event ledger first if it must be retained. All routing alternatives remain immutable for the duration of an admitted via.

## Executed 2200-tick WASM benchmarks (same initial conditions)

| Metric | SHEET98 demand-normalized | SHEET99 deadline-first |
|:--|--:|--:|
| Normal modeled ACKs | 403 | 403 |
| Normal worst silo admitted p95 | 75 ticks | **74 ticks** |
| Synchronized stress ACKs | 456 | **458** |
| Synchronized upstream cumulative wait | 23,254 lane-ticks | **22,359 lane-ticks** |
| Synchronized worst silo p95 | **345 ticks** | **345 ticks** |
| Synchronized clearance deferrals | **6,287** | 6,869 |
| Synchronized 96-tick late admissions | not tracked | **88** |
| Uneven-demand modeled ACKs | 449 | **450** |
| Active admitted route collisions | 0 | 0 |

The worst stress p95 did **not** improve and simulated clearance pressure **increased**; these failures remain part of the audit. "ACK" means a modeled in-process acknowledgment, not a network acknowledgment. Clearance measures 3D simulation polylines, not PCB fabrication, electromagnetic signal integrity, or solid swept-volume collision safety.

## Tests and run

- `node test_wasm.js` → **67/67 executed assertions**, checking nine domains/120 identities, route immutability, ACK conservation, D8 queue occupancy, deterministic reset/replay, and **strict age-ordering of admitted pending requests**. The deadline miss counter is explicitly checked to be nonzero under load.
- `node test_svg_dom.js` → **94/94 checks** with the *actual embedded WASM*, mock DOM, 600 animation frames / 1200 engine ticks. This is not browser paint.
- `python test_browser.py` → **real Chromium PASS**, no page errors, 72 toroids, 88 copper lines, 120 packet markers, 8 FIFO slots, skew/stress controls and screenshots.
- `clang --target=wasm32 -O2 -fno-builtin -nostdlib -Wl,--no-entry -Wl,--export-all -Wl,--strip-all -o kernel.wasm kernel.c` rebuilds the freestanding wasm32 binary. `python make99.py` rebuilds the standalone `index.html` with embedded WASM, provided that template/parent viewer is available as described in `make99.py`.

Files: `index.html`, `kernel.c`, `kernel.wasm`, `test_wasm.js`, `test_svg_dom.js`, `test_browser.py`, `make99.py`, `results.json`, `summary.json`, `browser_results.json`, viewer screenshots and `SHA256SUMS.txt`. The HTML is self-contained and can be opened directly as a file, with no HTTP server. The SVG is a 2D projection of the synthetic 3D model. Source and results are append-only, not replacements for SHEET98.