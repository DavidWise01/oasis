# OBF2 TCP Runtime Race v2.2 — Rust vs C++ vs Node

**Build and real loopback TCP tests: PASS** on GitHub Actions: https://github.com/DavidWise01/oasis/actions/runs/38509270216

Artifacts: https://github.com/DavidWise01/oasis/actions/runs/38509270216/artifacts/11869525392

The unchanged frozen dual-floor v0.7 SHA-256 is `47d4c89ac8155b9470852e0e23d2c059ad087eedc2b7949632a9431b5792fd4b`; the existing v2.1 regression passed **4,633 assertions**. Compilers: Rust 1.99.0, g++ 13.3, Node 22.23.3. Three implementations use the same OBF2 v2.1 12-byte header, two independently recovered rails, CRC32, maximum 65,536-byte source, and byte-for-byte re-encoding. All reject invalid CRC, unsupported version and contradictory rails. No frozen files changed.

## Fairer end-to-end comparison

One persistent TCP socket per runtime, one outstanding request, localhost 127.0.0.1, 10 warm-ups per size, single GitHub-hosted Ubuntu runner. Each request sends the complete OBF2 frame, the server validates, recovers, independently re-encodes and returns an identical OBF2 frame. All bytes are compared with the frozen Node v2.1 reference. Timings include client/socket/server work, not connection establishment.

| Input / OBF2 frame | Samples | Rust median / p99 | C++ median / p99 | Node median / p99 |
|---|---:|---:|---:|---:|
| ASTROPHAGE 214 B / 444 B | 250 | **0.0345 / 0.2118 ms** | 0.0356 / **0.0532 ms** | 0.0550 / 0.1396 ms |
| 4,096 B / 8,208 B | 110 | **0.0732 / 0.1080 ms** | 0.2501 / 0.2710 ms | 0.1168 / 0.1546 ms |
| 65,536 B / 131,088 B | 24 | 1.4146 / 1.4292 ms | 4.2328 / 4.2749 ms | **1.0959 / 1.3047 ms** |

Measured p95 times respectively:
- Rust: 0.0555, 0.1000, 1.4256 ms
- C++: 0.0425, 0.2650, 4.2630 ms
- Node: 0.0710, 0.1448, 1.1774 ms

Single post-benchmark process **RSS snapshot**: Rust 3,572 KiB; C++ 4,280 KiB; Node 96,536 KiB. These are not peak-memory numbers, and Node includes runtime overhead. Application throughput for the 65 KiB size (frame bytes delivered divided by wall time of serial request/reply): Node ~112.3 MiB/s, Rust ~88.4 MiB/s, C++ ~29.5 MiB/s. Values are not line-rate measurements and exclude request/response overhead bytes in the numerator.

## Interpretation

- **Rust**: best of three at 4 KiB; effectively tied for the smallest median. Low RSS at snapshot.
- **C++**: tightest p99 at 214 B and low RSS. Large-frame implementation is notably slower and should be optimized before eliminating it.
- **Node**: fastest at 65 KiB but far higher baseline RSS.
- **No universal winner yet**. The workload includes 250/110/24 measurements, so p99 especially at 24 samples is not robust; CI runner scheduling/jitter can move the rankings.

## Engineering next target (v2.3)

1. For Rust, remove per-message BTreeMap lock and vector clone of up to 65,536 map indices. Use immutable cached Arc maps or fixed-size direct permutation.
2. For C++, reduce allocations and vector copies for large buffers; reuse scratch arrays and cache positions without reallocation.
3. For Node, avoid accumulated Buffer.concat copies when backpressure or fragmentation grows; enforce a bounded receive buffer.
4. Repeat 5 independent randomized-order runs and report **p50/p95/p99**, peak RSS, steady-state memory, CPU, and queue saturation. Then run cross-host tests with controlled packet loss, delay, jitter and disconnections.

**Boundaries:** The benchmark validates classical deterministic OBS dual-rail message recovery and accidental-corruption rejection, *not* sender authenticity or source truth. CRC32 is not cryptographic authentication, and classical mirroring does not establish quantum entanglement or eliminate physical transmission time. The 444 B frame is specific to the canonical 214 B ASTROPHAGE field.
