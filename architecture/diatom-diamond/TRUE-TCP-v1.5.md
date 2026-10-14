# OBS v1.5 — true TCP streaming of the SAME OBS frame stream

**Scope:** Real `net.createServer` / `net.createConnection` over IPv4 loopback (`127.0.0.1`). Same lazy `tokenAt(i)` generator, the same 32-token frames, the same `obs-stream-v1.3.mjs` frame codec, and immutable dual floor v0.7. This is CPU-based symbolic token routing, **not** LLM inference or experimental quantum hardware.

## How to reproduce

Node 22.16.0, Python 3. All files needed for local replay are included.

```sh
node tcp-stream-v1.5.test.mjs
python3 tcp-matrix-v1.5.py
node tcp-stream-v1.5.mjs --tokens=20000 --compression=deflate --window=2 --mode=none
node tcp-stream-v1.5.mjs --tokens=20000 --compression=deflate --window=2 --mode=sha256d --delay=5
```

The benchmark binds to localhost only, creates an actual TCP listening socket on an ephemeral port, then sends *length-prefixed serialized OBS frames*. Each frame contains the original codec's full positive and negative rail coordinates. Four-byte network-length headers protect record boundaries; the receiver checks length, schema, frame sequence, token order and the independent end-to-end SHA-256 *comparison* before reporting success. Source tokens are generated lazily and never stored as a full input array.

A **two-frame application-level ACK credit window** provides bounded logical producer lead even with compression, because compressed network writes alone can be buffered extensively by the OS. `windowFrames=0` disables credit control for testing TCP's native write/drain behavior. The ACK is ordinary flow control and not a signature, witness, or authentication. Zero authenticating/endorsing witnesses are required.

`compression=deflate` uses Node zlib `deflateRawSync` level 1 per record, with a decompressed-frame output cap of 512 KiB. This is simply a wire-format option; the underlying OBS tokens, frames, frozen permutation, and address domains are unchanged. `mode=sha256d` is an optional Bitcoin-style **double SHA-256 checksum** recomputed by the receiver; it is not encryption or proof of who sent the record.

## Measured results

The included `tcp-results-v1.5.json` is the full nine-case run on Node v22.16.0 / Linux (same container platform). Each line ran in a new Node process; warmups precede the measured cases. These are **single-run measurements**, not confidence-bounded medians or an apples-to-apples controlled WAN throughput experiment.

| Case | Logical tokens/s | Frames | Wire bytes | Peak generated lead |
| --- | ---: | ---: | ---: | ---: |
| In process / 20K | 4,072 | 625 | n/a | 33 |
| TCP raw / 20K | 3,719 | 625 | 65,711,950 | 97 |
| TCP deflate / 20K | 3,492 | 625 | 1,107,638 | 97 |
| TCP deflate + SHA-256d / 20K | 3,235 | 625 | 1,135,929 | 97 |
| TCP deflate + 5ms/frame sink / 20K | 2,783 | 625 | 1,107,669 | 97 |
| In process / 100K | 4,163 | 3,125 | n/a | 33 |
| TCP deflate / 100K | 3,671 | 3,125 | 5,551,573 | 97 |

Raw OBS frame JSON is much larger than the source token text because the full mirrored enormous decimal addresses are included on the wire. Compression reduced TCP wire bytes by **98.31%** on the 20K workload, at a measurable CPU cost on this machine.

The 100K TCP run recovered **all 100,000 tokens** in order; the in-process pipeline was 11.8% faster in this run. p95 measured `sentAt -> consumed` latency on the 100K TCP run was ~17.46 ms. Both sender and receiver share one host and one process, so this is not a WAN latency measurement, and sampled heap/RSS include both endpoints.

## Failure and containment tests

`tcp-stream-v1.5.test.mjs` passes 19 assertions: tail frame, 2-frame credit window, compressed SHA-256d verification, no-ACK mode, mutated payload, sequence jump, truncated trailing frame, unsupported configuration and bad addresses. Complementary `true-stream-tests.mjs` from the v1.4 baseline passes 23 tests. Frozen v0.7 floor source SHA-256 is `47d4c89ac8155b9470852e0e23d2c059ad087eedc2b7949632a9431b5792fd4b` and is unchanged.

## Caveats

- TCP loopback is a real OS TCP socket and flow control protocol but not a remote network; route RTT, jitter, loss, congestion and encryption are untested.
- A generated lead bound of 97 tokens was **observed** for the 2-frame setting on tested workloads; it is not a formal resource proof for all inputs or OS buffers.
- Memory figures are sampled, not instantaneous process-wide peak and not proof of bounded memory across indefinite runtime.
- Checksums do not authenticate senders; no wallet keys, mining, signatures or consensus are involved.
- This v1.5 adapter is additive; no changes to frozen KET, v0.7 dual floor, v1.1 OBS core, v1.2 token bus, or v1.3 frame encoding.