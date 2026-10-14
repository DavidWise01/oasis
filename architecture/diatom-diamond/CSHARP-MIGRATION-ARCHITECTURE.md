# OASIS / KET — OBS token processing architecture, runtime inventory, C# target

## Source-of-truth audited on 2026-10-13

Repository: `DavidWise01/oasis`, directory `architecture/diatom-diamond/`.
Current tested processing baseline: Node.js v22.16.0, JavaScript ESM modules v0.7/v1.1/v1.2/v1.3/v1.4/v1.5. Separate Three.js browser HTML is a visualization frontend. **There is no LLM tokenization or neural inference in the OBS stream.** Token means user-defined symbolic token: `AaaA...ZzzZ`, a canonical nonnegative decimal string, or one Unicode punctuation/symbol scalar.

## The full pipe

```text
        SOURCE (lazy tokenAt(i) generator / token array)
               |
               v
      CANONICAL TOKEN VALIDATOR
         - letters (26 AaaA...ZzzZ)
         - canonical decimal nonnegative integers (text)
         - one Unicode non-letter/number/whitespace scalar
               |
               v
         STREAM BUFFER (v1.3)
       <=32 tokens / <=32,768 UTF-8 source bytes
       <=4,980 UTF-8 bytes per token
               |
               v
         FROZEN FLOOR v0.7
       UUDDLRLRBASS five passes
               |
       +-------+-------+
       |               |
    P(tokens)      P^-1(reverse(tokens))
       |               |
       v               v
    UTF-8 chunks     UTF-8 chunks
       |               |
       +-------+-------+
               |
          OBS v1.2 PACK
         o = type ordinal 0..27
         b = per-token fragment index
         s = 256^N + big-endian UTF-8 fragment
         chunk <=1245 bytes
               |
       +-------+-------+
       |               |
     d+ cells       d- cells reversed and complemented
       |               | using v1.1 O-1-o,B-1-b,S-1-s
       +-------+-------+
               |
          v1.3 FRAME HEADER
           sequence, token count,
           input UTF-8 size, fragment count
               |
          v1.5 TCP ADAPTER
           - JSON record containing BOTH rails
           - optional raw DEFLATE level 1
           - optional SHA-256/d/tagged checksums
           - 4-byte big-endian length + payload
           - localhost Socket + ACK credit <=2 frames
               |
           RECEIVER
           - length/schema/sequence checks
           - decompress / verify checksum if enabled
           - unmirror / unpack UTF-8 / invert BOTH rails
           - compare recovery and expected token sequence
               |
            SINK
        Recovered input + metrics
               |
             THREE.JS
       OBSIDIAN faceted shells and 5-turn helices
       (viewer only; not kernel compute)
```

## Stage-to-file map

| Layer | JavaScript source | Target C# component |
| --- | --- | --- |
| Frozen token/5-pass floor | `frozen/dual5-floor-v0.7/dual5.mjs` | `ObsKernel.Kind`, `Operation`, `Transform` |
| Big integer address space | `obs-core-v1.1.mjs` | `System.Numerics.BigInteger`, `Encode`, `Decode`, `Mirror` |
| 2-rail typed token bus | `obs-token-bus-v1.2.mjs` | `PackTokens`, `UnpackTokens`, `Bind`, `Recover` |
| Bounded stream frames | `obs-stream-v1.3.mjs` | `MakeFrame`, `RecoverFrame`, `ObsStreaming.EncodeAsync` |
| Local producer/consumer | `true-stream-benchmark.mjs` | bounded `Channel<ObsFrame>` capacity 1 |
| Real TCP loopback | `tcp-stream-v1.5.mjs` | next: `TcpListener`/`TcpClient`, `NetworkStream`, 2-frame ACK |
| Optional Bitcoin-inspired hash | `bitcoin-hash.mjs` | next: `SHA256.HashData`, optional transport feature |
| Display | `obs-stream-threejs-v1.3.html` | Three.js remains browser JavaScript |

## Core numerics

`o=10^10, b=100^100=10^200, s=1000^1000=10^3000`. Combined Cartesian symbol capacity is `10^3210` (3,211 decimal digits) but is *not* allocated; a coordinate can be a 3,210-digit index at the upper bound. `o` stores 0..25 letters, 26 numbers, 27 specials; `b` stores fragment index; `s` stores a sentinel-prefixed UTF-8 fragment.

`encode(o,b,s) = ((o * 10^200 + b) * 10^3000 + s)`.

`mirror(o,b,s) = (10^10-1-o,10^200-1-b,10^3000-1-s)`.

Frozen operator mapping: U rotate right 1, D rotate left 1, L pair-swap from slot 0, R pair-swap from slot 1, B reverse, A rotate right 2, S permutation no-op in the OBS hot path. Inverse reverses operation order and reverses U/D/A rotation direction. Input frames are independent; their transformations are **not equivalent to one monolithic permutation** of the whole token stream.

## What runs where today

- All authoritative source/permutation/packing/network and benchmark code runs **CPU-side in Node.js 22.16.0**, verified on Linux x86_64 container. JavaScript `BigInt` is the exact integer engine.
- TCP tests use actual IPv4 loopback sockets (`127.0.0.1`), with both endpoints on the same machine. They do not measure Internet packet loss, separate computer throughput or NAT/firewall behavior.
- Three.js uses JavaScript/WebGL in the **browser** to display 3D symbolic geometry. It does not feed GPU results back into the processor's canonical token transform. CDN-loaded WebGL rendering remains unverified in this container.
- The user's proposed C# target should run the authoritative kernel in a .NET 10 x64 process on Windows/Linux. Keep GPU rendering separate; do not imply an RTX 4050 is processing token math today.
- v0.8 quantum-state calculations and v0.9 visual noise metrics are separate simulations, **not in the hot token-processing path**.
- Historical checkpoint/witness v1.0 is **not an active OBS v1.1/v1.5 requirement**. Optional SHA-256d is an unkeyed transport checksum, not encryption or signer authentication.

## v1.5 benchmark (one-off single-run; not a C# result)

| Case | Tokens/sec | Wire bytes |
| --- | ---: | ---: |
| 20k in-process | 4,072 | N/A |
| 20k TCP raw JSON | 3,719 | 65,711,950 |
| 20k TCP deflate | 3,492 | 1,107,638 |
| 20k TCP deflate + SHA-256d | 3,235 | 1,135,929 |
| 20k TCP deflate + 5 ms/frame sink | 2,783 | 1,107,669 |
| 100k in-process | 4,163 | N/A |
| 100k TCP deflate | 3,671 | 5,551,573 |

On the 100k TCP run, 3,125 frames were recovered, max two unacknowledged frames, and 97 observed generated-token lead. This is a *bounded transport workload observation*, not a proof of constant process memory for all inputs. Neither tokens/s number is LLM-model inference speed.

## C# build status

The included .NET 10 C# source is a **reference port candidate** for v0.7-v1.3. A .NET SDK is not installed in the source-authoring environment, so neither build nor C# runtime parity/benchmark has been performed. A Node-generated fixture and independent Python oracle are included. Do not call the C# code production-ready without compilation, .NET tests, exact cross-language fixture checks and a v1.5 TCP transport port.