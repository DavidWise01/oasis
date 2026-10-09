# OaSIs SHEET 103 — 120-Lane Dot–Photon Attachment (single WASM module)

**Append-only successor integrating actual SHEET 101 + SHEET 102; not an overwrite of either.**

Topology: `8:0:8:0:8:0:8`, eight physical silo domains D0–D7, nine toroidal addresses per silo (72), eleven copper sublayers per silo (88) centered on `{{-1::0::+1}}`, one logical aggregate D8 with eight FIFO slots and two service workers, immutable lane identities `0..119`. SHEET 101 causal deadline commitment filter, 3D bent-path clearance reservation, geometric recovery, congestion, synthetic modeled ACKs and conservation rules are preserved.

## The new constant, executable

`one successful via hop = one local photon dot tick` and `v ∈ Z^8`; initial `v=[1,2,3,4,5,6,7,8]`. The carrier has a full `2³ = 8` addressable state space, **not eight spawned photons**. Its linear transition is a permutation matrix `P_delta` with `P_delta e_j=e_(j XOR delta)` for `delta=from XOR to`. The eight-component state is queried as `v[j] = (j XOR mask) + 1`. This is mathematically identical to the explicit eight-entry vector shuffle in SHEET 102, because `mask ^= delta` composes successive transforms. Every lane's vector therefore retains `sum(v)=36`, `sum(v²)=204`, and all eight distinct components across hops. The `mask` is three bits in the value domain 0–7, held as a WASM integer; lane identity remains unchanged.

A **photon dot tick is distinct from a SHEET 101 scheduler tick**: the former advances on successful completed movement across a via, while the latter covers any time spent in clearance-hold, 24-tick via animation, 8-tick aggregate service and 5-tick modeled receipt-to-ACK latency. D8 pending service does not increment a phantom photon tick. For a floor hop, graph addresses use the source and destination silo indices in `0..7`. For a copper hop, use the source/destination physical copper sublayer indices modulo eight; adjacent conductor movement is a weighted neighbor edge even over the 7→0 wrap. This mapping is a **symbolic addressing adapter**, not an assertion about the physical copper sheet carrying real photons at discrete jumps.

### Network cost

The exact SHEET 102 deterministic network edge graph is used: ring adjacencies `i ↔ (i+1) mod 8`, opposite chords `i XOR j=4`, cost `c(i,j)=1+((3·min(i,j)+5·max(i,j)) mod 4)`. Costs are *nonnegative weights independent from elapsed simulation ticks*. Total network cost is the sum across actual committed via hops. The 101 path optimizer still selects among its four safe physical via polylines; this integration does **not** claim it finds globally minimum weighted network cost routes. The two network address types (floor versus conductor) are explicitly tagged by the existing `kind` field.

### State and performance strategy

The implementation uses **one freestanding C/WASM executable**, not 120 separate WASM instances, and no JS-side 120×8 data warehouse. Each lane has an O(1) XOR-mask update and an O(1) network-edge cost update on a completed via. The viewer expands a selected lane's eight state components on demand; the WASM test also checks all of them. No new packet IDs are allocated or sent through D8. The memory optimization pertains to the eight-state transform itself; extra audit counters have storage cost and no end-to-end CPU speed-up is asserted without matched throughput benchmarking.

### Executed verification

Compiled clang wasm32 build, test against the actual prior SHEET 101 compiled binary using identical policy, workers, clock and scenario inputs. The integrated binary passed **251,616 deterministic assertions** across normal, synchronized 120-lane stress, uneven-demand skew and replay. At every tested checkpoint the legacy ACKs, waiting, geometry conflicts, FIFO occupancy, deadline classifications, delivered count, and per-lane floor/phase/copper state match SHEET 101. All 120 vectors are permutations of `1..8` with preserved sum and squared norm and globally conserved dot and cost counters; `total photon dot ticks == completed vias` at each measured checkpoint.

| 2200 scheduler ticks | Normal | Stress | Skew |
|---|---:|---:|---:|
| Completed photon dots / vias | 1331 | 1253 | 1341 |
| Weighted network cost | 2770 | 2610 | 2790 |
| Modeled ACKs (same as SHEET101) | 403 | 458 | 450 |
| Aggregate upstream waiting lane-ticks (same) | 5360 | 22359 | 7399 |

A real Chromium run via Playwright executed the **embedded WASM** in the HTML, rendered 72 toroid SVG groups and 120 lane markers, inspected all eight state components, selected lanes and reset the state; synchronized test finished with 1,253 dots, 2,610 cost, 458 ACKs and no page errors. Chromium `file://` navigation is blocked in the testing environment, so the test feeds the *unaltered HTML bytes* into the browser via `page.set_content`, which executes the same inline JS and embedded WASM. The standalone HTML requires no network fetch.

### Reproduce

```sh
clang --target=wasm32 -O2 -fno-builtin -nostdlib \
  -Wl,--no-entry -Wl,--export-all -Wl,--strip-all -o kernel.wasm kernel.c
python build_viewer.py
node --check inline.js       # after extracting the inline script if rebuilding
node test_wasm.js             # keep parent101.wasm alongside for independent baseline
python test_browser.py       # requires Chromium and Python Playwright
```

`compose103.py` reconstructs the two changes (C entry-point attachment + SVG inspector) deterministically from the parent SHEET101 files if those are at `../sheet101`. The ZIP ships standalone `kernel.c`, `kernel.wasm`, compiled binary in HTML, `parent101.wasm` reference, source and tests; no parent folder is required to run or reproduce the compiled target. `SHA256SUMS.txt` lists exact file digests. The in-session event ledger may be exported; reset intentionally starts a fresh session.

**Limits:** This is a symbolic deterministic carrier model, not quantum electrodynamics, physical photon velocity, 3D PCB manufacturing clearance, real networking acknowledgments, or a new proof of simulation theory. Eight integer components and permutation matrices do not alone establish a physically normalized quantum state.