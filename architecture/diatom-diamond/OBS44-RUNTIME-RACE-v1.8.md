# OBS44 Runtime Race v1.8 — matched benchmarks

Reproducible CI run: https://github.com/DavidWise01/oasis/actions/runs/38494831932

## Scope

262,144 OBS44 glyphs per timed run, 32-token frames, 5 timed runs on the same GitHub Ubuntu runner. Each implementation executes the exact frozen `UUDDLRLRBASS ×5` positive and inverse dual-rail permutations, independently inverts both rails, verifies exact recovery, and calculates the same FNV-1a order-sensitive checksum `1923136285`. Timed loops exclude startup and compilation. This is **classical OBS44 byte-token processing**, not LLM inference or a full TCP benchmark.

| Runtime | Median glyphs/s |
|---|---:|
| C++ | 15,605,281 |
| Rust | 14,284,121 |
| C | 12,069,848 |
| Go | 5,159,161 |
| C# / .NET 10 | 2,881,885 |
| Node.js 22 | 1,828,423 |

All six agree on the same checksum, checked against the Python reference. The in-repository `.github/workflows/obs44-runtime-race-v1.8.yml` and `runtime-race-v1.8/` contain the compiled Rust, C#, Node, C, C++, and Go sources and reproduction job.

Additional *different-machine* local comparisons tested Java (~2.67M glyphs/s), Swift (~1.73M), Python (~230K), PHP (~217K), and Ruby (~64K). These are not part of the matched GitHub ranking; local samples used a separate environment and in some cases different sample counts.

## Key findings

- C++ is **8.5% faster** than Rust by the two matched medians on this one workload. This is not a universal statement about the languages.
- Rust is a strong **network-facing kernel candidate** thanks to competitive native performance and memory-safety without garbage collection. The raw throughput winner is C++, not Rust.
- The original 60-step operators can be compiled into a position map for each packet size without changing behavior. A local Python oracle checked 26,000 equivalence assertions for frame lengths 0..64.
- Actual OBS codec `BigInt`, large coordinate serialization, compression, socket buffering, packet loss, end-to-end recovery, and latency have **not yet been tested across C++ and Rust**. The earlier Node TCP v1.5 benchmark is a separate data point.
- A source-of-truth network must distinguish integrity (matching bytes), source authentication/trust, and semantic truth. A noncryptographic FNV test checksum does not authenticate messages.
- A classical dual-rail network does **not** establish experimentally confirmed quantum entanglement. No programming language or Planck-scale address eliminates network propagation delay or relativistic time effects.

**Engineering recommendation:** build and test an additive Rust daemon for the real transport path, keep C++ as a competing optimized core, preserve frozen v0.7 and OBS44 registry, and advance only after measuring p50/p95/p99 latency, throughput, memory, backpressure and corruption recovery on the same test network. No signed-witness quorum or checkpoint subsystem is required by this proposal.
