# SHEET 162 — Measured Benchmark & Verification Report

**Result:** 24/24 new mTLS integration checks, 19/19 batch-store unit checks, and 36/36 inherited SHEET 161 mTLS checks passed independently. Full historical regression chain was not executed. One host only.

## Same-source A/B network comparisons

| Metric | 512 recovered | 1,024 recovered |
|---|---:|---:|
| Source records | 640 | 1,152 |
| Starting target count | 128 | 128 |
| S161 legacy recovery | 3.752 s | 7.958 s |
| S162 batched, keep-alive | 2.242 s | 4.614 s |
| S161 throughput | **136.45 rows/s** | **128.68 rows/s** |
| S162 throughput | **228.37 rows/s** | **221.96 rows/s** |
| Observed speedup | **1.67×** | **1.73×** |
| Batched segment writes | 64 | 128 |
| Batched head writes | 64 | 128 |
| TLS connections | 3 | 3 |
| Network requests (optimized) | 133 | 261 |
| Network response bytes | 685,159 | 1,450,571 |
| Historical record hashes replayed | 0 | 0 |

The two alternatives used the **same exact source data, two source certificates, independently signed anchor, record index, and pinned local mTLS network**. The baseline ran **first** in each case, so thermal, cache and scheduling effects could favor the second run. This is an observational comparison, not randomized statistically controlled benchmark.

## Crash and integrity evidence

* 19 local batch tests verify exact byte-equivalent segment digest and Merkle root versus S160 sequential appends; 256-record boundary and cross-boundary refusal.
* A segment write completing before the head is quarantined. Matching two-operator Ed25519 approval can reconcile its exact committed segment. One or forged approvals fail.
* A new witness died as a separate process immediately after persisting an eight-record batch but **before returning the acknowledgement**. On restart the original nonce and source checkpoint were retained and the remaining rows completed without duplication.
* Signed S161 proof, nonce, external floor and full Merkle append-chain checks remain active. Existing S161 gate rerun exits 0 (36/36).
* Response-side TCP reuse was observed as **3 sockets across 133 or 261 requests**, while node count and certificate identities were held constant.

## Concurrency and atomicity limits

A batch is atomic with respect to one 256-record segment and a cooperative, local file lock. It is **not** a multi-host distributed transaction. A segment has to be durably written before its head; a crash in between requires explicit operator-reviewed reconciliation (fail-closed). Head and segment are not simultaneously fsynced in one hardware transaction; storage controllers may still lie about durability. Each source retains independent Ed25519 identity but ran on the same physical host. Segment reads retain S160's digest checks; the ordinary proof path is index-based rather than whole-history replay.

## Reproduce

```bash
cd sheet162
node unit162.js
node gate162.js
# Short smoke-only mode:
S162_FAST=1 S162_SKIP_CRASH=1 node gate162.js
```

The benchmark generator writes `benchmark162.json` and uses disposable OpenSSL CA and mTLS credentials. Tests require Node 22+, OpenSSL, and POSIX fsync behavior. Raw logs are included in the release.