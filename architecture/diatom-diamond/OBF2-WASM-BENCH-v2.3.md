# OBF2 v2.3 — WebAssembly execution target

**Independent GitHub Actions PASS**: https://github.com/DavidWise01/oasis/actions/runs/38510593902

The module is a real freestanding WebAssembly MVP binary compiled from `obf2-wasm-v2.3/obf2_wasm.c` via Clang (`wasm32`, no libc, no imports, stripped). GitHub Actions independently rebuilt it and cross-tested it against the frozen v2.1 dual-rail transport reference. The frozen v0.7 SHA-256 was verified; no frozen code was changed.

- WASM module size **3,761 bytes**.
- Fixed linear memory **2,097,152 bytes (2 MiB)**; payload cap **65,536 bytes**; OBF2 frame cap **131,088 bytes**.
- Exported ABI: `input_ptr`, `frame_ptr`, `recovered_ptr`, `max_bytes`, `encode(n)`, `decode(frame_len)`.
- **5,071 GitHub CI assertions PASS** including randomized, empty, UTF-8, max-size, byte-for-byte parity, CRC error and dual-rail mismatch rejection.

## Reproducible compute comparison

The GitHub runner measured 5 alternating timed sweeps of `encode + decode` including host memory copying. Figures are median microseconds per encode/decode pair; no TCP sockets in this table.

| Input size | WASM hosted by Node 22 | Native JavaScript |
|---|---:|---:|
| 214 B ASTROPHAGE | 3.521 μs | 4.869 μs |
| 4,096 B | 58.529 μs | 72.704 μs |
| 65,536 B | 916.844 μs | 1129.759 μs |

A separate local benchmark produced different rankings for larger buffers (64 KiB: WASM ~1312 μs, JS ~1260 μs on its first run). Differences across machines and jitters prohibit universal speed claims.

## Node-host TCP comparison (local host; five alternating sweeps)

Sequential single-outstanding-request loopback TCP, with an identical Node socket adapter hosting either WASM or JS. Bytes cross from the JavaScript host into the WASM memory when selected; WASM does not itself have browser TCP sockets. Both implementations recovered the original field exactly and rejected corrupt frames.

| Input | WASM TCP median / p99 | JS TCP median / p99 |
|---|---:|---:|
| 214 bytes | 0.05975 / 1.69077 ms | 0.07317 / 1.24273 ms |
| 4 KiB | 0.19064 / 2.08371 ms | 0.19347 / 2.14382 ms |
| 64 KiB | 2.26601 / 7.56613 ms | 1.76925 / 4.18202 ms |

These timings are local host only and should not be compared as if they were the same-runner v2.2 native Rust/C++ experiment. Small samples and scheduler jitter make the tail statistics exploratory.

## System alignment

```text
OASIS/KET frozen
  -> {{i}} 42 identities × 8 views -> typed ASTROPHAGE field
  -> existing OBF2 v2.1 dual 5-pass reversible permutation + CRC32
  -> native Rust/C++ server OR portable WASM codec in Node/browser/edge host
  -> platform network interface (TCP from Node/Rust/C++; WebSockets or WebTransport from browsers)
  -> exact source-byte recovery
```

**Recommended split:** keep a native network host (prefer the best measured Rust or C++ service), expose the exact OBF2 pure byte codec as WASM for browsers and other hosts. WASM is a compilation/runtime target, not a direct replacement for every host socket API. A browser WASM client can use `WebAssembly.instantiate` / `instantiateStreaming` to load the module, but it needs its JavaScript/host layer to communicate.

The self-contained offline HTML demo is included in the downloadable v2.3 release ZIP with the actual embedded WASM bytes. We could not run the page in headless Chromium in this restricted container because local file and localhost navigation were denied by browser administrator policy. Do not construe the Node tests as a successful browser integration test.

This benchmark tests **classical deterministic recoverability**, not source authenticity, factual truth, physical entanglement or absence of propagation time. CRC32 only detects accidental corruption.

**Next performance work:** eliminate duplicate host→WASM copies, optimize maximum frames, compare true native Rust versus Rust-compiled WASM in one CI workload, and run cross-host traffic with loss/jitter/backpressure before production.
