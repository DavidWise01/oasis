# SHEET 100 — Deadline Feasibility / Impossible-Certificate WASM Test

**Canonical topology preserved:** `8:0:8:0:8:0:8`, eight silo domains D0–D7 with nine toroids each (three X, three Y, three Z²), eleven copper sublayers each (−5 through +5, center `{{−1::0::+1}}`), one *logical* D8 aggregate, eight FIFO slots, two parallel logical workers (configurable to one), 120 immutable lane IDs. No physical PCB clearance or real networking is claimed.

This is an **append-only** successor to SHEET99. It does not silently transform the 96-tick *soft admission objective* into a guaranteed SLA. In fact it formally rules out some promises by comparing demand with an **optimistic capacity ceiling** directly in the compiled WASM kernel. A capacity test which does not rule out a deadline is **NOT** a positive guarantee of success. Physical via clearance, admission bottlenecks and new competing work can still cause misses.

## Model and definitions

Hypothetical counterfactual: `N` transactions become **eligible at the aggregate D8 at the same instant**, starting empty with `W` workers. Each worker requires `S=8` ticks per committed handoff, the modeled ACK takes `A=5` ticks, and D8 has `Q=8` slots.

For a deadline horizon `T >= 0`, **optimistic upper bounds** (deliberately ignoring single-admit-per-tick and interference) are:

- **Queue admissions:** `Q + W * floor(T/S)`.
- **Committed handoffs:** `W * floor(T/S)`.
- **Modeled ACKs:** `W * floor(max(0,T-A)/S)`.
- **Earliest ideal all-batch modeled ACK:** `S * ceil(N/W) + A` for `N>0`.

If `N` exceeds any ceiling, that objective is **PROVEN IMPOSSIBLE** inside this hypothetical capacity model. Otherwise return `NOT RULED OUT` rather than `guaranteed`. The bounds are one-sided necessary conditions, not a sufficiency theorem. `N=120`, `T=96`, `W=2` yields ceilings 32 / 24 / 22, and earliest ideal final ACK tick 485. One worker yields 20 / 12 / 11 and tick 965. This is based on complete simultaneous *D8 readiness*, whereas the actual `Stress 120` button primes simultaneous **via requests** that complete their 3D clearance and enter D8 over multiple ticks. Do not confuse the two tests.

The following exports implement the pure certificates, with finite-input guards: `get_hypothetical_admission_ceiling`, `get_hypothetical_commit_ceiling`, `get_hypothetical_ack_ceiling`, `get_burst_impossible_flags` (1=admission, 2=handoff, 4=ACK), `get_burst_min_ack_ticks`, `get_burst_min_commit_ticks`, `get_feasibility_model_version`.

## Actual compiled WebAssembly test

`node test_wasm.js` performs **40/40 explicit assertions** plus per-tick population/identity/conservation/queue/clearance checks at five reproducible checkpoints in each scenario. All scenarios ran **2,200 ticks** using real `wasm32` bytecode:

| Run | ACK | Admissions later than 96 ticks | Worst silo p95 (ticks) | Total upstream wait (lane-ticks) |
|---|---:|---:|---:|---:|
| Normal, two workers | 403 | 0 | 74 | 5,360 |
| Synchronized via requests, two workers | 458 | 88 | 345 | 22,359 |
| Uneven via requests, two workers | 450 | 35 | 169 | 7,399 |
| Synchronized via requests, one worker | 271 | 259 | 792 | 104,523 |

All 120 lane identities preserved, no admitted synthetic swept-polyline conflicts at tested checkpoints, D8 occupancy ≤8, population of D0..D8 conserved, `committed+pending=aggregate admissions`, and modeled `ACK+pending=destination receipts`. The burst two-worker run has reproducible SHA256 end-state replay. This is not a complete proof against all possible execution traces.

`node test_regression99.js` reruns the **67/67 SHEET99 comparison suite** against the *new* SHEET100 binary. Historical counts from SHEET99 remained unchanged, including 458 stress ACKs and 88 deadline misses. `python test_browser.py` launches real Chromium via Playwright, renders the 72 toroids, 88 traces, 120 lane dots and the feasibility panel, changes hypothetical request size and worker count, runs stress and skew, tests the flags and records browser screenshots: **21 checks; no page errors**.

## Reproduce locally

```bash
clang --target=wasm32 -O2 -fno-builtin -nostdlib -Wl,--no-entry -Wl,--export-all -Wl,--strip-all -o kernel.wasm kernel.c
python3 build_viewer.py
node test_wasm.js
node test_regression99.js
python3 test_browser.py   # requires Playwright and Chromium
```

The standalone `index.html` embeds the compiled WASM binary: opening it directly requires no local HTTP service. Its live SVG feasibility panel allows adjustable `N`, `T`, and 1-vs-2 workers. Historic kernels are not modified; audit data are append-only within a run until the user chooses reset. The source, WASM, build instructions, tests, screenshots, full result JSON and per-file SHA-256 checksums are in the downloadable ZIP. No real-world delivery ACK, electromagnetic safety, full 3D collision volume, or hard bounded SLA is demonstrated.