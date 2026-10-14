# ASTROPHAGE FIELD — OBF2 Compact Network Transport v2.1

**Status:** additive optimization, frozen OASIS/KET / `{{i}}` / dual5 / OBS source unchanged. No witness/signature/checkpoint requirement.

## Solved bottleneck

The canonical 214-byte ASTROPHAGE field becomes **698,894 bytes of decimal OBS dual-rail JSON** or **2,557 bytes under raw Deflate** with the v2.0 implementation. The new OBF2 protocol sends the same two independently recoverable byte-token permutations in **444 bytes**. It reconstructs the huge `o/b/s` addresses when needed, instead of serializing the `10^3000` complemented seed as 3,000 decimal digits per cell.

The maps are compiled from the unchanged `UUDDLRLRBASS ×5` frozen operation implementation for each bounded packet length, then cached. The negative byte order matches exactly the mirrored/reversed physical rail of v2.0. For numeric-byte OBS tokens, full legacy `{o,b,s}` values can be reproduced deterministically; the regression verifies **every one of the 214 physical negative cells**, not just output text equality. Generic OBS token kinds require their existing v1.2 encoder, and this profile is not a replacement for it.

### OBF2 frame

```
Bytes: 4 MAGIC "OBF2" | 1 VERSION | 1 FLAGS | 2 RESERVED |
       4 N (uint32 BE) | N BYTES d+ | N BYTES d- |
       4 CRC32 (uint32 BE)
Wire bytes = 16 + 2N; N ≤ 65,536
```

The two rails must invert to identical original bytes. The field-specific decoder additionally enforces exact UTF-8 and canonical ASTROPHAGE grammar. CRC32 detects accidental errors but **does not authenticate senders**, establish factual truth, prove quantum entanglement or bypass propagation delays. No signatures or witnesses have been added.

### Local Node.js 22.16.0 results

| Metric | v2.0 Deflate | v2.1 OBF2 |
|---|---:|---:|
| Wire bytes | 2,557 | **444** |
| Median TCP request latency (localhost) | 17.21 ms | **0.54 ms** |
| p95 TCP latency | 21.96 ms | **0.95 ms** |
| p99 TCP latency | 26.83 ms | **1.27 ms** |
| Median single-process CPU decode (fields/s) | ~58 | **~18,502** |

Loopback TCP: 60 repeated connections per mode, alternate order, 4 warmups. CPU decode: 5 timed samples per mode, 6 legacy decodes and 10,000 OBF2 decodes per sample, measuring the entire respective decode and field parser. These are *same-machine implementation* comparisons and **not** claims about wide-area TCP, different language speeds, or neural inference.

**Regression:** 4,633 assertions including 2,000 seeded round-trip messages; full-size 65,536-byte frame; every original physical negative mirrored OBS coordinate; source-view checks; CRC and truncation rejection; frozen SHA-256 check `47d4c89ac8155b9470852e0e23d2c059ad087eedc2b7949632a9431b5792fd4b`. Known limitation: CRC32 cannot reject a coordinated adversarial change to both rails with a recomputed CRC.

## Run

```bash
node architecture/diatom-diamond/astrophage-compact-v2.1.test.mjs
node architecture/diatom-diamond/astrophage-compact-v2.1.bench.mjs
```

Implementation: `astrophage-compact-v2.1.mjs`. Benchmark outputs `benchmark-results-v2.1.json` in the same folder. The old v2.0 ASTROPHAGE field and OBS libraries remain required as read-only imports.

## Next target

Test the same OBF2 protocol in Rust, C++ and Node.js on matched hardware over a real two-machine link; measure end-to-end throughput, p50/p95/p99, allocations, backpressure and byte-perfect recovery. This benchmark is not a physics or quantum experiment.
