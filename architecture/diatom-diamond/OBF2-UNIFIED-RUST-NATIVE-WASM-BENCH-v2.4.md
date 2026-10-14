# OBF2 v2.4 — One Rust kernel, two compilation targets

**Independent GitHub Actions: PASS**  
Run: https://github.com/DavidWise01/oasis/actions/runs/38518114163  
Compiled WASM and machine-readable CI artifacts: https://github.com/DavidWise01/oasis/actions/runs/38518114163/artifacts/11872901402

## Reproducibility and architecture

`obf2-rust-dualtarget-v2.4/kernel.rs` is **one Rust source file** containing the exact OBF2 binary codec, frozen five-pass `UUDDLRLRBASS` permutations, CRC32, dual-rail recovery, bounded input (65,536 bytes) and frame (131,088 bytes). The same `Codec` implementation is compiled as:

- **Linux-native optimized Rust** binary and a TCP server (standard library, no external crates).
- **`wasm32-unknown-unknown` WebAssembly** module, called from a minimal Node.js TCP host.
- Node.js JavaScript v2.1 is the independent reference.

The frozen v0.7 floor SHA256 remains `47d4c89ac8155b9470852e0e23d2c059ad087eedc2b7949632a9431b5792fd4b`. The existing v2.1 regression passes **4,633 assertions**, including 2,688 `{{i}}` route checks. The new WASM parity suite passes **8,030 assertions**, including randomized round trips and rejection of bad CRC, rail discrepancies, and unsupported versions. All network servers pass the same cross-encoding and injected-fault suite.

## True apples-to-apples TCP benchmark

The three servers ran **on one GitHub Ubuntu runner**, each bound to loopback `127.0.0.1`, with one persistent connection and one request in flight. Each request contains the complete OBF2 frame. The server validates CRC and both rails, fully recovers the bytes, rebuilds OBF2 and returns it for byte-for-byte comparison with the reference. Connection startup is excluded from timing. One client with 10 warmups per size, **250 / 110 / 24 timed requests**.

| Input / wire frame | Native Rust median / p95 / p99 (ms) | Rust→WASM via Node median / p95 / p99 (ms) | Node.js reference median / p95 / p99 (ms) |
|---|---:|---:|---:|
| Canonical ASTROPHAGE 214 B / 444 B | **0.0434 / 0.0527 / 0.0628** | 0.0513 / 0.0699 / 0.1216 | 0.0640 / 0.0938 / 0.1481 |
| 4,096 B / 8,208 B | **0.0871 / 0.0996 / 0.1019** | 0.1109 / 0.1393 / 0.1441 | 0.1320 / 0.1762 / 0.1842 |
| 65,536 B / 131,088 B | **0.9680 / 1.0015 / 1.0435** | 1.1956 / 1.2144 / 1.2147 | 1.2379 / 1.2809 / 1.3715 |

At all three sizes native Rust has the best median *in this run*. Rust WASM comes second. **Tail measurements with only 24 large-frame samples are not stable p99 estimates**; treat these as exploratory CI values.

## Matched codec operation microbenchmark (five sweeps)

Median microseconds for **encode + decode**, excluding TCP. Rust native directly invokes the same `Codec`; WASM passes through Node.js and copies data across the host/module boundary; JavaScript v2.1 runs in Node.js. The native 214-byte fixture was synthetic, while WASM/JS used the canonical 214-byte field. Length and algorithm are matched, but this is not strict payload-byte parity for the native 214-byte microbenchmark; the TCP test above *is* strict payload parity.

| Frame source bytes | Native Rust | Rust WASM | Node.js JavaScript |
|---:|---:|---:|---:|
| 214 | **2.060 μs** | 2.586 μs | 3.557 μs |
| 4096 | **38.96 μs** | 44.29 μs | 59.79 μs |
| 65536 | **623.53 μs** | 689.86 μs | 861.48 μs |

## Footprint and constraints

Rust WebAssembly module: **1,662,183 bytes**, initialized linear memory **2,097,152 bytes**, linker maximum **8 MiB**. Unlike the previous C-to-WASM proof of concept (3,761 bytes), this Rust `std` build carries substantial language-runtime code; byte-for-byte comparable functionality does not imply equal binary size.

The Linux Rust executable was approximately 4.5 MiB on disk. One post-benchmark RSS snapshot: native Rust 2,328 KiB; the Node process hosting Rust WASM 92,452 KiB; the Node JavaScript server 96,468 KiB. Host RSS cannot be interpreted as only WASM linear memory, and these snapshots are **not peak-memory metrics**.

## Recommendation and next performance target

**Candidate production shape: Rust-native TCP/QUIC service, same Rust codec compiled for WASM clients**. Keep the previous tiny C-to-WASM binary as a footprint comparator for embedded/browser cold start; do not deprecate other languages solely from one runner. The current Node/WASM interface copies input and output buffers; the next optimization is a borrowed-memory interface where possible, multi-connection backpressure, repeated randomized benchmark batches, and **cross-machine tests with measured loss, delay and jitter**.

These tests establish **classical deterministic OBF2 packet agreement**, *not* sender authenticity or semantic truth. CRC32 only detects accidental corruption. Classical duplicate rails are not physical quantum entanglement. No language or transport removes physical propagation delay.

**Frozen KET, `{{i}}`, OBS floor, ASTROPHAGE grammar and OBF2 v2.1 remain unchanged**; all v2.4 code is additive.
