# P3.27 — Cached versus streamed Stargate execution

Date: 2026-10-09. Primitive `-+- /\\ +-+` retains one even and one odd arm, one pinned root, and the unitary mixing convention of P3.26.

Executed local Node.js v22.16.0 benchmark using the P3.26 local kernel. Six sizes tested. The cached implementation precomputes gate descriptors; streamed regenerates descriptors per position. At all five comparable sizes, output amplitudes matched exactly (maximum component difference 0). Forward/inverse and norm checks passed for all six.

| Stages | Stream forward+inverse ms | Cache build ms | Cached forward+inverse ms | Inverse error |
|---:|---:|---:|---:|---:|
| 3 | 0.213 | 0.075 | 0.090 | 2.78e-17 |
| 99 | 0.420 | 0.029 | 0.939 | 8.88e-16 |
| 999 | 2.288 | 0.184 | 1.546 | 1.42e-14 |
| 9999 | 13.255 | 1.929 | 12.174 | 1.70e-13 |
| 99999 | 24.395 | 14.102 | 42.820 | 1.66e-12 |
| 999999 | 174.546 | not run | not run | 1.66e-11 |

Maximum observed norm discrepancy 1.66e-11. One wall-clock observation per configuration. Timings are sensitive to JIT compilation, thermal state, system load, runtime and GC; **do not treat these as calibrated performance measurements**. Streaming does not store per-stage descriptor arrays. Cached descriptors consume memory proportional to N; process RSS does not isolate this allocation. The 999999-stage test does not establish a failure threshold.

The full local benchmark and results are supplied as downloadable files in the conversation. GitHub contains a compact reproducible benchmark module implementing the same mathematical comparison, but remote CI of that file remains unverified.

Next target P3.28: capture independent repeat timings, compare error drift against N, and add authenticated/checkpointed replay that detects incorrect restoration of retained channels.
