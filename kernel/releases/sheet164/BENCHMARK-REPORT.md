# SHEET 164 — Factorial Benchmark Report

**Status:** 68/68 new checks PASS; inherited SHEET 163 gate 45/45 PASS in isolated snapshot, exit 0.

## Protocol and experiment design

- Three independent factors: prefetch window `{1,4}` × durable record batch `{4,8}` × pinned mTLS reuse `{off,on}` = **8 conditions**.
- Two reproducibly shuffled blocks, seed `0x164bad5`; each condition recovers the same 128-record suffix from a 384-record source.
- Signed quorum proof pages, authenticated SHA-256 Merkle extensions, and exactly ordered segment/head fsyncs remain active in every condition.
- Synthetic page completion jitter is deterministic, 3–14 ms according to offset and block; no simulated multi-host network or remote storage.
- Each condition begins with a fresh 256-record target copied from one verified seed. Timing includes recovery handshakes and RPCs but excludes the setup/seed copy.
- The mTLS-off branch creates new authenticated TLS connections per request and **keeps certificate pinning enabled**.

## Observed throughput

| Prefetch | Batch | Reuse TLS | Block 1 rec/s | Block 2 rec/s | Mean/median rec/s | TLS connections/request |
|---:|---:|:---:|---:|---:|---:|:---|
| 1 | 4 | off | 125.23 | 154.81 | **140.02** | 37/37, 37/37 |
| 1 | 4 | on | 197.49 | 193.48 | **195.49** | 3/37, 3/37 |
| 1 | 8 | off | 170.49 | 160.97 | **165.73** | 37/37, 37/37 |
| 1 | 8 | on | 171.28 | 196.89 | **184.08** | 3/37, 3/37 |
| 4 | 4 | off | 330.44 | 318.72 | **324.58** | 37/37, 37/37 |
| 4 | 4 | on | 348.59 | 500.69 | **424.64** | 5/37, 5/37 |
| 4 | 8 | off | 285.97 | 383.84 | **334.90** | 37/37, 37/37 |
| 4 | 8 | on | 382.11 | 566.59 | **474.35** | 5/37, 5/37 |

## Factor-level marginal means (descriptive, not causal confidence intervals)

| Factor | Low condition | High condition | Difference (records/s) |
|---|---:|---:|---:|
| window | 171.33 | 389.62 | +218.29 |
| batch | 271.18 | 289.77 | +18.59 |
| reuseTls | 241.31 | 319.64 | +78.33 |

Highest two-trial median: **4/8/true → 474.35 records/s**. Lowest median: 1/4/false → 140.02 records/s. Their cross-factor ratio is 3.39×, **not** a controlled estimate of any single optimization.

## Holdout and crash injections

- Chosen policy: `{"batch": 8, "reuseTls": true, "window": 4}`.
- Independent holdout: **136 rows**, **0.2566 s**, **530.10 records/s**. Starts at 248 to exercise segment rollover.
- Actual child-process kill after durable segment/head persistence but before the acknowledgement; restart resumed the original signed transaction and converged to the correct Merkle root without duplicates.
- The crash test’s reported post-restart duration **excludes the pre-crash period**, so it is not directly comparable to the factorial throughput figures.

## Verification and limits

- 68/68 new checks, exit 0. A separate untouched snapshot of SHEET 163 passed 45/45, exit 0.
- Every measurement is one-host loopback mTLS with synthetic keys and local disk. TLS connections are authenticated even when reuse is disabled.
- The selected policy was chosen from just two repetitions per configuration: selection bias, caching, and run-order effects remain possible.
- All 16 factorial runs use the same source history and shared source processes, limiting repeated setup variance but not eliminating host scheduling noise.
- The proof page is still a bounded 8-record unit; the 4-record factor splits already-verified pages into smaller durable commits.
- Crash injection covers one chosen policy; it is not a proof of all possible power failures, multi-host partitions, or Byzantine behavior.
- Cross-host consensus and the unresolved historical SHEET 142 timing-sensitive assertion are not claimed fixed.

## Exact reproducibility

```bash
node gate164.js
python make_docs164.py
python browser-check164.py
bash run-inherited163.sh
```

Raw machine-readable measurements: `benchmark164.json`; command logs: `gate164.log`, `audit/inherited163.log`.