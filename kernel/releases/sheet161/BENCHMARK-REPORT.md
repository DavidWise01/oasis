# SHEET 161 — Empirical Benchmark Report

**Captured:** 2026-10-09 (America/Chicago). **Environment:** Node.js 22.16.0, one physical host, three separately running localhost mTLS processes, local filesystem. **Claim:** locally reproducible measurements, not a multi-host performance guarantee.

## Recovery throughput

| Workload | Source records | Start prefix | Records recovered | Signed pages | Recovery (s) | Records/s | Mean page (ms) |
|---|---:|---:|---:|---:|---:|---:|---:|
| Small | 640 | 32 | 608 | 76 | 4.683 | 129.84 | 61.61 |
| Medium (instrumented) | 2,048 | 1,024 | 1,024 | 128 | 9.386 | 109.10 | 73.33 |
| Large | 4,096 | 3,072 | 1,024 | 128 | 8.307 | 123.28 | 64.90 |

The small and large workload results are from the prior 35-check implementation; the instrumented medium run includes a **36th rollback-sequence check** and captures transfer bytes and RSS. Performance differences are not attributable to one cause without repeated statistical runs.

## Instrumented medium workload

- **1,024 rows recovered** in **9.38576 s**, or **109.10 rows/s**.
- **128 pages** transmitted, with exactly 8 entries per full page.
- **1,433,259 bytes** of signed JSON page responses (approximately 1.37 MiB); mean **11,197.3 bytes/page**; max **11,425 bytes/page**. Other TLS and protocol overhead is not included in this byte count.
- **63.22 MiB RSS** measured for the recovering witness process near completion.
- **0 history record hashes replayed** on the ordinary source/recovery path, according to S160's instrumented `recordHashesReplayed` counter. This does not mean zero disk I/O or zero hash computation.
- Crash injected *after a durable record append but before acknowledgement*, then the target restarted and resumed without duplicate rows.

## Comparison to SHEET 160

- Existing SHEET 160 benchmark file records **12,288 records**, **619 durable appends/s**, **~1,158 bytes per inclusion proof**, and **0 hot-path historical replay** in its earlier standalone test.
- This is **not an apples-to-apples speed comparison**: SHEET 160 measured local append performance, while SHEET 161 includes pinned mTLS network requests, signed source proofs, verification, and target fsync writes.
- A fresh SHEET160 regression gate passed **71/71**, and migration bridge passed **19/19**. The fresh 12,288-record benchmark rerun exceeded its execution limit after around 6,144 appends; do not treat its historical result as newly confirmed.

## Security/regression report

- **SHEET161: 36/36 passed** on the final run; other two workloads each passed 35/35 under the prior instrumented assertions.
- **SHEET160: 71/71 gate, 19/19 migration bridge passed** in a copied predecessor directory.
- **Entire inherited historical chain:** not rerun; no full-chain pass claim.
- Rejected one-signer quorum, duplicate signer, forged anchor, forged page, substituted leaf, altered inclusion sibling, altered Merkle extension, out-of-order page, replay after finalization, unpinned TLS client, and valid-but-stale anchor epoch.

## Complexity and next bottleneck

Proofs use indexed subtree lookups from a 256-row segment store and the S151 binary-peak hash tree, avoiding full-history record hashing on ordinary proof operations. End-to-end recovery still costs **O(missing records)** in bytes and work; every recovered row is individually fsynced and indexed. The current one-request-per-page TLS handshake and synchronous fsync write path dominate throughput. Next: batched durable transactions with a single properly atomic segment+head update, connection reuse, and pinning across independently operated hosts.