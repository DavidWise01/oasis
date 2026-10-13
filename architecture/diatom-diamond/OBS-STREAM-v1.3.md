# OASIS / OBS v1.3 — Framed stream core + inference-rate terminology

**Additive release, no mutations to immutable v0.7 floor, OBS v1.1, or v1.2 bridge.**

`OBS` capacities remain `o = 10^10`, `b = 100^100 = 10^200`, `s = 1000^1000 = 10^3000`; the coordinate product `10^3210` is symbolic address capacity, not RAM or physical qubits.

## Implementation

`obs-stream-v1.3.mjs` exposes `makeFrame`, `decodeFrame`, `encodeStream`, `decodeStream`, `inspectStream`, `pointForCell`, `capabilities`.

- Frames include sequence, token count, UTF-8 byte count, fragment count and a v1.2 dual packet. Every frame runs `UUDDLRLRBASS × 5` per rail from the frozen floor.
- The adaptor buffers at most **32 typed tokens**, **32,768 UTF-8 bytes per frame**, and **4,980 UTF-8 bytes per token**; errors are explicit if a single token exceeds this streaming profile.
- The source generator/consumer can be unbounded but a producer must supply finite tokens. The benchmark prebuilds the input array; that external memory is not bounded by the adapter.
- A v1.2 full-message permutation and a v1.3 sequence of per-frame permutations are not the same encoded object. Both decode to the identical input tokens. Frame headers prevent ambiguous ordering; no security witness/checkpoint/cryptographic audit system is introduced.
- `pointForCell` maps exact arbitrary-precision coordinates to schematic 3D positions via modular reductions. This projection is non-injective and must not be used to decode tokens.

## Throughput and what "inference" means

**There is no neural-network model inference in this source.** For reproducibility, the benchmark defines *one symbolic routing operation* as encoding and decoding one typed logical token via both rails, and reports logical tokens/sec, OBS cells/sec, frames/sec, latency per batch, and sampled process heap delta. These figures cannot be compared as LLM output tokens/sec or physical quantum computations/sec.

Node.js benchmark: warm-up 1 run plus 5 sequential timed runs per configuration; simple mix of canonical letters, integer strings, 0 and Unicode symbols. Timing is host/hardware dependent and ratios vary with input sizes, V8 runtime state and GC. The baseline is v1.2 whole-packet bind/recover; the streaming mode is v1.3 framed 32-token encode/decode; these have the same recovered output but *different encrypted/permuted frame representations*. Heap figures are snapshot estimates at frame boundaries, not accurate allocator high-water marks.

Run:

```sh
node obs-stream-v1.3.test.mjs
node --expose-gc inference-benchmark.mjs
python browser-smoke.py
```

### Measured local results

| Input logical tokens | v1.2 tokens/s (median) | v1.3 tokens/s (median) | v1.3 / v1.2 | v1.3 frames |
|---:|---:|---:|---:|---:|
| 512 | 5,466 | 5,641 | 1.03× | 16 |
| 2,048 | 5,811 | 5,387 | 0.93× | 64 |
| 8,192 | 5,585 | 5,186 | 0.93× | 256 |

Local test suite passed 9,556 assertions in 135 scenarios. System Chromium passed 14 UI checks using the offline Canvas fallback. The included Three.js/WebGL module depends on an online CDN and could not be confirmed in the restricted browser.

## Release scope

- `obs-stream-v1.3.mjs`: bounded async iterable token streaming API
- `obs-stream-v1.3.test.mjs`: regression, fragmentation and deliberate corruption tests
- `inference-benchmark.mjs` + `benchmark-results.json`: reproducible throughput runs
- `obs-stream-threejs-v1.3.html`: orbitable three-shell obsidian geometry, dual rails, frame slider, token/cell inspector; network-dependent WebGL and tested offline projection
- `browser-smoke.py`, `viewer-preview.png`: interactive fallback check and preview

No physical quantum computing, entanglement measurement or inference-model output is claimed.
