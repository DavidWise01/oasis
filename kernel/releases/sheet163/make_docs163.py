from pathlib import Path
import json, statistics, hashlib, platform
P=Path(__file__).resolve().parent
bench=json.loads((P/'benchmark163.json').read_text())
rows=bench['allResults']; cond=bench['conditions']; find=lambda name:next(x for x in rows if x['name']==name)
report='''# SHEET 163 — Parallel Merkle Prefetch / Adaptive Segment Batching

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
'''
for x in cond:
 report+=f"| {x['trial']} | {x['latencyMs']} ms (every third page) | {x['serialRowsPerSecond']:.2f} records/s | **{x['parallelRowsPerSecond']:.2f} records/s** | **{x['ratio']:.3f}×** | {' → '.join('parallel' if w==4 else 'serial' for w in x['order'])} |\n"
report+='''
**Interpretation:** This is an observed local A/B comparison (two conditions, one paired repetition each), not a population-level speedup guarantee. The fixed eight-record batches and persistent pinned TLS configuration are held equal within each pair, isolating speculative proof fetching as the primary changed variable. Workloads ran sequentially and may be affected by cache, disk, CPU, and event-loop variability.

## Batch-size and segment-boundary observations

| Scenario | Records | Commit size | Duration | Rate | Segment/head commits |
|---|---:|---|---:|---:|---:|
'''
for n,label in [('trial1-w4','Fixed 8; four fetches'),('batchsize-fixed4','Fixed 4; four fetches'),('boundary-prefetch','Adaptive 3 at boundary, then 8')]:
 r=find(n);report+=f"| {label} | {r['recovered']} | {r['batchMode']} | {r['durationMs']:.2f} ms | {r['recordsPerSecond']:.2f}/s | {r['segmentCommits']} / {r['headCommits']} |\n"
report+='''
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
'''
(P/'BENCHMARK-REPORT.md').write_text(report)
arch='''# SHEET 163 — Complete ASCII Execution and Fault Process

```text
                              OASIS / ROOT0
                                    |
                  FROZEN SHEET 162 STORAGE / WITNESSES
                                    |
                         SYNCHRONIZATION REQUEST
                                    |
                   +----------------+----------------+
                   |                                 |
             RESOURCE BLUE                    SOURCE RED + GREEN
                   |                                 |
       mTLS CLIENT CERT + SERVER PIN          SIGNED HEAD FETCH
                   |                                 |
             LOCAL DURABLE HEAD <---- 2/3 CERTIFIED RESOURCE HEAD
                   |                                 |
          VERIFY EXISTING SESSION             ANCHOR FLOOR CHECK
                   |                                 |
          PIN EXTERNAL CHECKPOINT              EPOCH / ROOT / COUNT
                   |                                 |
          PERSIST NONCE + TARGET <----------- SAME VERIFIED TARGET
                   |
             BOUNDED FETCH WINDOW
                   |
          +--------+--------+--------+--------+
          |        |        |        |        |
        PAGE n   PAGE n+1 PAGE n+2 PAGE n+3  ...
          |        |        |        |
        FETCH    FETCH    FETCH    FETCH  (parallel network reads only)
          |        |        |        |
          +--------+--------+--------+
                   |
           OUT-OF-ORDER ARRIVAL
                   |
            ORDERED PAGE BUFFER
                   |
             REQUIRE CURSOR n
                   |
              VERIFY SIGNER
                   |
          VERIFY INCLUSION + EXTENSION
                   |
          VERIFY LOCAL PEAK FRONTIER
                   |
         CHOOSE ADAPTIVE BATCH 1..8
                   |
         LIMIT TO 256-SEGMENT BOUNDARY
                   |
          +--------+--------+
          |                 |
        NORMAL            INVALID
          |                 |
   EXCLUSIVE WRITER LOCK   REJECT / NO WRITE
          |
      WRITE SEGMENT
          |
      FSYNC SEGMENT
          |
     PERSIST MERKLE INDEX
          |
        WRITE HEAD
          |
       FSYNC HEAD
          |
     SIGN DURABLE STATUS
          |
          +----------+-----------------+
          |                            |
        ACK                         CRASH / LOST ACK
          |                            |
   ADVANCE CURSOR               RESTART TARGET
          |                            |
      PREFETCH NEXT         READ SIGNED DURABLE CURSOR
          |                            |
          |                       COUNT ADVANCED?
          |                            |
          |                  +---------+----------+
          |                  |                    |
          |                 YES                   NO
          |                  |                    |
          |         DISCARD STALE PREFETCH    FAIL CLOSED
          |                  |
          +------------------+
                   |
            REFETCH FROM CURSOR
                   |
           VERIFY FINAL ROOT
                   |
             SIGNED FINISH
                   |
             NEXT VERIFIED
```

ADVERSARIAL MATRIX
  A1  remote pages reordered                 -> ordered commits only
  A2  malicious/invalid signed pages         -> fail closed in base verifier
  A3  segment boundary at cursor 253         -> 3-row fragment then full batches
  A4  crash after 8-row fsync, before ACK    -> restart and no duplicate
  A5  stale but signed external floor        -> SHEET 161 pin rollback rejection
  A6  concurrent speculative reads           -> no speculative durable writes
  A7  server identity substitution           -> mTLS fingerprint pin rejects
  A8  conflicting recovery session           -> reject mismatched nonce/target
  A9  segment persisted, head not committed  -> existing SHEET 162 quarantine

STORAGE COSTS
  BATCH_8   segment fsync + head fsync, once each per 8 records
  BATCH_4   segment fsync + head fsync, once each per 4 records
  BOUNDARY  truncate at segment capacity, never mix two physical segments

METRIC TERMS
  RPS = successfully recovered records / elapsed synchronization seconds
  MAX_IN_FLIGHT = number of concurrent page fetch promises
  NETWORK_BYTES = signed HTTP response bytes on mTLS connection
  SOCKETS = new socket objects, *not* independently measured handshakes
  DURABLE_COMMITS = count of completed segment and head fsync operations
```
'''
(P/'KERNEL-ASCII.md').write_text(arch)
(P/'KERNEL-ASCII.txt').write_text(arch)
readme=f'''# SHEET 163 — Parallel Merkle Fetch / Ordered Durable Commit

**Release status:** dedicated new gate **45/45 PASS**; inherited SHEET 162 storage **19/19** and SHEET 162 network **24/24** PASS on separate runs. The **complete historical lineage was not rerun**.

This additive extension preserves the entire SHEET 162 source tree in `baseline162/`. The principal new modules are:

- `pipeline163.js` — bounded parallel signed-proof fetch, strict ordered commit cursor, recovery after lost ACK, mTLS socket reuse.
- `node163.js` — backward-compatible protected resource with `/apply163`, receiver-side signature/proof verification, segment-boundary and batch-hint enforcement.
- `gate163.js` — reproducible one-host mTLS correctness, crash and randomized-order benchmark harness.
- `benchmark163.json` and `BENCHMARK-REPORT.md` — measured trial detail with benchmark limitations.
- `KERNEL-ASCII.txt` — complete execution, proof, persistence and recovery pipe.
- `index.html` — interactive SVG fault and benchmark dashboard.

## Baseline A/B

Source: **528 journal records**, target begins at **128**; each run recovers **400 records** with eight-record durable writes on both sides.

| Condition | Serial window 1 | Parallel window 4 | Speedup |
|---|---:|---:|---:|
'''
for x in cond:readme+=f"| Trial {x['trial']}, delay {x['latencyMs']} ms | {x['serialRowsPerSecond']:.2f}/s | {x['parallelRowsPerSecond']:.2f}/s | {x['ratio']:.3f}× |\n"
readme+='''
The A/B order is pseudo-randomized with a fixed seed, and one condition simulates 14 ms of delayed page completion. Treat these as local observations, not speed guarantees. The four-record batch comparison also ran faster than fixed-eight in one run, demonstrating that fewer fsync calls need not guarantee better throughput.

## Execute

```bash
node gate163.js
bash run-new.sh
```

No external JavaScript dependencies; Node.js 22, OpenSSL, POSIX filesystem semantics, and loopback networking were used. Running the full historical lineage can be costly and is not represented as completed here. Testing cannot prove independent-host consensus or physically separate rollback-fence enforcement.
'''
(P/'README.md').write_text(readme)
print('docs created',[(n,(P/n).stat().st_size) for n in ['README.md','BENCHMARK-REPORT.md','KERNEL-ASCII.txt']])
