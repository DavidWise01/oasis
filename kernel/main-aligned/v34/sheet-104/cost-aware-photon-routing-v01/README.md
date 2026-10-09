# OaSIs • SHEET 104 — Cost-Aware 3D Dot–Photon Routing

Append-only successor to **SHEET 103**, retaining one box `8:0:8:0:8:0:8`:
8 physical silos D0..D7, 9 toroids per silo (3 X/3 Y/3 Z²), 11 copper sheets per silo L−5..L+5, one logical D8 aggregate with eight FIFO slots and two workers, 120 stable lanes, one symbolic dot–photon carrier and 8-state vector per lane, and modeled destination receipts/ACKs.

## Change

SHEET 103 tests the full 3D clearance of up to four fixed-endpoint bent centerlines and commits the **first admissible** candidate. SHEET 104 can instead enumerate every admissible candidate and pick the lowest **combined estimated cost**:

`estimated_score_milli = round(1000 * (|source→midpoint| + |midpoint→target|)) + 1000 * photon_edge_toll(source_address,target_address)`

The edge toll is determined by the endpoints, so changing the geometric bend **cannot reduce the intrinsic photon toll**. The achieved savings are geometric route-length savings; not demonstrated shorter network time, electromagnetic efficiency or bandwidth. All candidates undergo the same full 3D conservative route-route clearance check against all currently active immutable 2-segment routes before selection. A selected route remains immutable during its 24-tick via. Mode 0 exactly reproduces SHEET 103's first-clear path selection; mode 1 minimizes route length among admissible paths, with deterministic mode-number tie breaking. Both preserve the same abstract photon 8-state XOR mask transformation, one logical dot per completed via, separate edge cost, bounded D8 queue, deterministic deadline-gate behavior, and all 120 lane IDs.

The score and length are accounted **when a via is granted**, while the intrinsic photon edge toll is accounted **when its hop completes**. Snapshots taken with in-flight vias therefore do not necessarily reconcile route-grant toll with completed-hop toll. `get_cost_savings_milli` compares each grant against the first admissible route **at the same time and active state**; it does not claim a one-to-one identical counterfactual history under the two policies.

## Executed tests

Both policies: identical initial traffic, 2200 ticks, single compiled WASM module, 3 cases.

| Case | First-clear total 3D route length | Cost-optimized route length | First-clear / optimized ACKs | First-clear / optimized intrinsic photon edge toll | Clearance deferrals first-clear / optimized |
|---|---:|---:|---:|---:|---:|
| Normal | 9320.982 | **5214.000** | 403 / 403 | 2770 / 2770 | 2042 / 2047 |
| Stress 120 | 9534.488 | **5808.600** | 458 / 458 | 2610 / 2610 | 6869 / 6869 |
| Uneven demand | 9740.528 | **5765.100** | 450 / 450 | 2790 / 2790 | 4512 / 4512 |

`node test_wasm.js`: **494,975 assertions passed** across normal, stress, skew, and deterministic replay; full 2³ vector permutation, 120 lane identities, domain conservation, D8 FIFO capacity and ACK identity, one dot per via, route immutability, 3D clearance, and nonnegative savings.

`node test_regression.js`: **157,197 assertions passed** compared with the exact earlier compiled SHEET 103 `kernel.wasm` at many checkpoints, confirming baseline mode preserves the source kernel's lane, ACK, waiting, route, geometry, scheduler and photon state.

`python test_browser.py`: **real Chromium passed**, no page errors, 72 toroid SVG groups, 88 copper lines, 120 markers, eight photon graph nodes, live cost chart and policy switch. Executing 2200 WASM ticks directly in Chromium reproduces stress ACK 458, photon intrinsic cost 2610, geometric length 9534.488 vs 5808.600, no active route-clearance conflicts. Chrome file:// access can be restricted by security policy; tester uses `page.set_content` to run the same self-contained HTML, while the viewer itself embeds WASM and needs no external fetch.

### Reproduce

```sh
clang --target=wasm32 -O2 -fno-builtin -nostdlib -Wl,--no-entry -Wl,--export-all -Wl,--strip-all -o kernel.wasm kernel.c
python build_viewer.py
node test_wasm.js
node test_regression.js
python test_browser.py
```

`index.html` can be opened standalone. The suite ZIP includes the exact executable and source, parent SHEET103 WASM solely for regression, tests, screenshots, results, source patch/build utilities, and `SHA256SUMS.txt`.

**Limits:** Synthetic geometric units, not literal physical copper clearance. No measured CPU speedup, physical photon tick, real network delivery ACK, real networking hop latency, PCB DRC, electromagnetic propagation, or real-life photon behavior is established. Old sheets remain untouched; upstream event ledger is in memory and must be exported before reset.