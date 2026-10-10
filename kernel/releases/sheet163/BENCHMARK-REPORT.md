# SHEET 163 — Parallel Merkle Prefetch / Adaptive Segment Batching

## Benchmark protocol

- One physical machine, real local mTLS client/resource processes; Ed25519 quorum heads and signed external anchor floor.
- Identical SHEET 162 indexed source journal (**528 records**); fresh target begins at **128 records** for A/B trials.
- Exactly **400 records recovered** in every matched A/B run; **fixed 8-record batches** on both sides, different fetch concurrency only (1 vs. 4).
- Deterministic pseudo-random trial order (seed `0x163d`), with trial 1 parallel-first, trial 2 serial-first.
- Trial 1 uses ordinary local requests; trial 2 injects 14 ms extra delay on every third page, modelling higher response latency (not a physical network delay).
- All transactions verify the same source root, all commit cursors increase, and the proof-verifier's historical-hash replay count remains zero.

## Matched A/B results

| Trial | Extra response delay | Serial window=1 | Parallel window=4 | Observed ratio | Order |
|---|---|---:|---:|---:|---|
| 1 | 0 ms (every third page) | 159.62 records/s | **298.71 records/s** | **1.871×** | parallel → serial |
| 2 | 14 ms (every third page) | 177.57 records/s | **329.52 records/s** | **1.856×** | serial → parallel |

**Interpretation:** This is an observed local A/B comparison (two conditions, one paired repetition each), not a population-level speedup guarantee. The fixed eight-record batches and persistent pinned TLS configuration are held equal within each pair, isolating speculative proof fetching as the primary changed variable. Workloads ran sequentially and may be affected by cache, disk, CPU, and event-loop variability.

## Batch-size and segment-boundary observations

| Scenario | Records | Commit size | Duration | Rate | Segment/head commits |
|---|---:|---|---:|---:|---:|
| Fixed 8; four fetches | 400 | fixed8 | 1339.08 ms | 298.71/s | 50 / 50 |
| Fixed 4; four fetches | 400 | fixed4 | 998.92 ms | 400.43/s | 100 / 100 |
| Adaptive 3 at boundary, then 8 | 275 | adaptive | 622.02 ms | 442.11/s | 36 / 36 |

The four-record run was **faster than the eight-record run** despite twice the number of commits. That result is retained as observed; this benchmark does **not** establish monotonic performance with batch size. The test beginning at record 253 exercises a 3-record boundary fragment before entering segment 256, with subsequent commits safely bounded to individual segments.

## Concurrency and proof correctness

- Source pages are fetched speculatively over pinned, persistent mTLS connections (bounded window 1–8).
- Page signatures, inclusion proofs, Merkle extensions, and the external anchor are checked before the target writes.
- Only the exact next cursor is sent for durable application; fetched responses may arrive out of order but commits cannot.
- A signed duplicate/replay is not blindly retried after an acknowledgement failure: the client re-reads the target's authenticated, durable cursor.
- A real process exited after fsync but before ACK, then restarted and completed without duplicate records.
- Existing SHEET 162 tests passed independently: **19/19 storage** and **24/24 network/crash**. New SHEET 163 gate: **45/45**. The full frozen SHEET 103–162 lineage was *not* freshly rerun.

## Limitations

- All test processes share one physical host and the same test CA; not independent-host network consensus.
- Connection metrics count **opened TLS sockets**, not packet-level or hardware-verified handshakes.
- Segment write and head persistence remain two distinct fsync transactions; interrupted writes may require quorum-reviewed reconciliation.
- A/B trials have only one sample per condition; variance and warm-cache effects can dominate.
- A further protocol change would be needed for true multi-host durability, remote storage barriers, and durable cross-host admission control.