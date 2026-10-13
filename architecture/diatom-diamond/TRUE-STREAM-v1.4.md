# OASIS / KET · OBS True Streaming v1.4

**Scope:** Production-style Node.js **object stream** backpressure bench for the previously published OBS v1.3 framed reversible token router; Bitcoin-inspired digest modes are strictly optional. **No neural-model inference, physical quantum device, Bitcoin network, encryption, cryptographic signatures, proof-of-work or external witnesses.** Frozen v0.7 `UUDDLRLRBASS × 5` source remains unchanged.

## What is actually streamed

```
lazy tokenAt(index) generator (no array of N input tokens)
    ↓ async iterable
v1.3 encodeStream(): max 32 canonical OBS tokens / <=32 KiB source UTF-8 per frame
    ↓ optional SHA-256 / SHA-256d / tagged SHA-256 digest attached by sender
Node Readable.from(..., {objectMode:true, highWaterMark:1})
    ↓ .pipe() / node:stream/promises.pipeline()
Node Writable({objectMode:true, highWaterMark:1})
    ↓ delayed consumer, including 5 ms / frame slowdown case
verify sender's optional hash, v1.3 decodeFrame(seq), compare every recovered token against deterministic expected input
```

- 100,000 tokens are produced **lazily**; the benchmark does not allocate a precomputed source-token array or retained output array.
- v1.3's per-frame permutation semantics are **not equal to one giant global permutation** over the full stream; frame boundaries remain explicit and deterministic.
- `pause` / `drain` events are instrumented. With a 5 ms delayed consumer, producer paused 626 times and the writable drained 625 times for 625 frames. Both queue high-water marks are 1 frame, with at most 65 generated but unconsumed tokens in this scenario.
- Source bytes count unencoded UTF-8 input tokens; transport is object-mode in one Node.js process, **not TCP, HTTP, disk I/O or network packet throughput**.
- RSS/heap memory high-water readings are samples every 20 ms. They do not prove absolute peak memory or process-level O(1) usage, because Node GC, decoder buffers, input frame representations, native allocator and OS caching also matter.

## Exact local measurements

Machine reported by Node v22.16.0: AMD EPYC 9V74, 4 available parallel processors. Each case was run in a **fresh Node process**, one run per configuration (not five-run medians). Results therefore include scheduling/GC noise; do not overinterpret close hash variants.

| Case | Tokens | Duration | Tokens/s | Frames | Pauses | Drains | Sampled RSS growth |
|---|---:|---:|---:|---:|---:|---:|---:|
| baseline | 20,000 | 3.79 s | 5,275 | 625 | 1 | 0 | 40.1 MiB |
| sustained | 100,000 | 17.98 s | 5,562 | 3,125 | 1 | 0 | 40.3 MiB |
| slow sink 5 ms | 20,000 | 4.57 s | 4,377 | 625 | 626 | 625 | 37.8 MiB |
| hash none | 20,000 | 3.58 s | 5,593 | 625 | 1 | 0 | 40.0 MiB |
| SHA-256 verify | 20,000 | 4.49 s | 4,453 | 625 | 1 | 0 | 41.8 MiB |
| SHA-256d verify | 20,000 | 4.32 s | 4,626 | 625 | 1 | 0 | 41.9 MiB |
| tagged SHA-256 verify | 20,000 | 4.24 s | 4,721 | 625 | 1 | 0 | 44.7 MiB |
| no-hash repeat | 20,000 | 4.03 s | 4,965 | 625 | 1 | 0 | 39.9 MiB |

These rates measure reversible OBS *symbolic throughput*, not LLM tokens/sec. For reproducible exact samples see `true-stream-results.json` and re-run the suite. The size of the object/JSON encoding includes very large decimal OBS addresses; byte rates are much lower than tokens/sec might suggest.

## Bitcoin cryptography (not encryption)

Bitcoin publishes its transactions; its block headers use double SHA-256 for proof of work and BIP-340 defines Schnorr signatures and tagged SHA-256 hashes. **Double SHA-256 does not encrypt anything.** Inspired only by those hash functions, the optional v1.4 adapter computes:

- `sha256`: SHA256(canonical version-tagged JSON frame)
- `sha256d`: SHA256(SHA256(the same bytes))
- `tagged`: SHA256(SHA256(tag) || SHA256(tag) || frame bytes), with tag `OBS/v1.4/Frame`
- `none`: no digest

Sender attaches a digest, consumer recomputes and checks it. This detects accidental changes *against the unmodified comparison digest*, but a malicious intermediary can simply recompute both. **No keys, signatures, consensus, Bitcoin wire protocol, or authenticated transport** are implemented. If we need *confidentiality*, use an authenticated-encryption scheme such as AES-256-GCM with secure key management; SHA-256 is not encryption. No such encryption is enabled here.

Official references: https://developer.bitcoin.org/reference/block_chain.html and https://github.com/bitcoin/bips/blob/master/bip-0340.mediawiki

## Commands

Requires Node >= 22 and Python 3 (Python only orchestrates distinct benchmark processes).

```bash
node true-stream-tests.mjs
node true-stream-benchmark.mjs --tokens=100000 --delay=0 --mode=none
node true-stream-benchmark.mjs --tokens=20000 --delay=5 --mode=none
node true-stream-benchmark.mjs --tokens=20000 --delay=0 --mode=sha256d
python run-matrix.py
python browser-smoke.py
```

`true-stream-threejs-v1.4.html` provides an interactive results dashboard. The **offline Canvas** selector passed four browser checks using system Chromium. A Three.js/WebGL rendering path is included but requires network-loaded modules and remains unverified here.

## Safety / version discipline

`v0.7 frozen`, `v1.1 core`, `v1.2 token bridge`, and `v1.3 stream` files are read-only dependencies; all v1.4 changes are additive. No cryptocurrency keys, wallet operations, external auditors or signatures. Runtime frame hashes are optional and **not** retrofitted into the core.
