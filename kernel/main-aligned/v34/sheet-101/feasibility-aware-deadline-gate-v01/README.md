# SHEET 101 — Feasibility-Aware Deadline Admission (WASM × SVG)

Append-only successor to **SHEET 100**. Canonical physical abstraction remains one `8:0:8:0:8:0:8` box, with eight floors = eight isolated silo domains D0…D7, nine symbolic toroids per floor grouped X/Y/Z² (72 total), 11 copper subplanes per floor with `{{−1::0::+1}}` at zero (88 total), and 120 stable packet/lane IDs. The D8 aggregate remains **logical**, not a ninth physical floor, with eight FIFO slots and two eight-tick service workers. Full 3D polyline clearance, 24-tick via transport, five-tick modeled ACK latency and append-only session event lineage are retained.

## The new gate — what it actually does

A D8-eligible request arrives after its physical via finishes. **Before putting it into the D8 waiting stage**, WASM calculates an optimistic lower bound for how soon its modeled ACK could complete:

```
remaining_work = 8 + Σ(8 − queue_entry_service_ticks) + 8 × older_eligible_waiters
optimistic_ACK_ticks = ceil(remaining_work / worker_count) + 5
```

This is a **necessary**, not sufficient, capacity test, because it ignores future arrivals, one-at-a-time queue admission and geometric contention. It is valid as an impossibility certificate for the *strict oldest-eligible-first* scheduler (fairness policy `3`). When the gate is switched on and the required scheduler is selected:

- **Candidate / not ruled out**: optimistic_ACK_ticks ≤ 96 ticks. No guarantee is issued, because additional limitations may still prevent meeting the target.
- **Capacity-infeasible**: optimistic_ACK_ticks > 96 ticks. The user-defined latency claim must not be promised; the request is still queued and processed normally, with full lineage.
- **Unchecked**: gate is switched off or a different scheduler is selected, for which the strict-oldest assumptions do not hold.

The gate changes which **deadline commitments are eligible**, **not which packets are admitted to the physical D8 queue**. It deliberately does not drop, reorder, or secretly throttle packets. This isolates the truthfulness of an SLA promise from throughput changes. A future sheet can add separate, evidence-tested physical admission control with explicit backpressure.

### ASCII

```
                8 : 0 : 8 : 0 : 8 : 0 : 8
           ┌──────── 8 SILOS / D0–D7 ────────┐
           │  each: 9 toroids × 11 Cu planes  │
           └─────────────────┬─────────────────┘
                             │ VIA COMPLETE
                             ▼
                  ┌─ D8 DEADLINE GATE ─┐
                  │ remaining workload │
                  │ vs 96-tick target  │
                  └──────────┬─────────┘
                   ┌─────────┴───────────┐
               CANDIDATE             INFEASIBLE
               NO GUARANTEE          NO PROMISE
                   └─────────┬───────────┘
                     SAME FIFO [0..7]
                        WORKER A/B
                           │
                     DESTINATION ACK
```

## Actual compiled-WASM comparison

All scenarios execute the **exact same WASM binary** and compare gate OFF (unchecked baseline) versus gate ON with identical simulation initial conditions, 2 workers, strict oldest-first fairness, adaptive clearance, and **2,200 ticks** per case.

| Observed measure | Normal | Synchronized via-request burst | Uneven-demand burst |
|---|---:|---:|---:|
| Modeled ACKs (same with gate OFF/ON) | 403 | 458 | 450 |
| Eligible D8 requests | 406 | 459 | 451 |
| Not-ruled-out candidates | 358 | 361 | 403 |
| Certificate says deadline impossible | 48 | 98 | 48 |
| Actually late ACKs in candidate group | 1 | 0 | 0 |
| Actually late ACKs in impossible group | 48 | 98 | 48 |
| All late ACKs (same as gate OFF) | 49 | 98 | 48 |
| Admitted 3D route conflicts | 0 | 0 | 0 |

A fourth one-worker stress test returned 271 ACKs, 308 infeasible classifications and 260 late ACKs in the infeasible completed group. **The gate does not reduce actual lateness**; it avoids making commitments that existing resource capacity disproves in advance. In normal load, one of the provisionally feasible ACKs still misses 96 ticks, showing why a passing *necessary* test cannot guarantee success.

**122/122 explicit executable WASM assertions** passed, alongside additional per-tick invariants: nine-domain conservation, queue ≤ 8, ACK accounting, 120 identity retention, replay, gate classification conservation, no confirmed infeasible request met its deadline, other-scheduler unchecked fallbacks, and unchanged throughput/wait between gate modes. Original SHEET99 regression: **67/67 PASS**. Chromium using embedded WASM and actual SVG: **21/21 PASS**, zero page errors; visually checked queue, gate mode switch, 72 toroids, 120 markers, 8 slots, normal/stress/skew controls and per-silo audit.

## Build and run

With clang WASM32, Node.js, Python3 and optionally Playwright Chromium:

```
clang --target=wasm32 -O2 -fno-builtin -nostdlib -Wl,--no-entry -Wl,--export-all -Wl,--strip-all -o kernel.wasm kernel.c
python build_viewer.py
node test_wasm.js
node test_regression99.js
python test_browser.py
```

Open `index.html` locally (all WASM bytes embedded). The “Capacity filter / Unchecked baseline” selector resets the current simulation session. Export the JSON event ledger to retain provenance beyond that session; reset intentionally clears in-memory events. The SVG panel renders gate classifications and per-silo counts and permits exporting the current SVG.

**Limitations:** The model is not physical PCB fabrication verification, not a real external ACK, not a hard deadline guarantee, and not a true network admissions gateway. The feasibility bound depends on the unchanged FIFO/oldest policy, no hidden work ahead, deterministic two-worker service and simulated timing units. The capacity-infeasible states are recorded; no previously appended sheet has been overwritten. Browser verified by loading exact HTML content into Chromium; filesystem `file://` navigation was blocked in the browser harness, but standalone-file embedding remains self-contained.