# SHEET 162 — Batched Segment Recovery / Persistent mTLS

**Status:** `0e / PASS` for **43/43 new checks** (19 storage + 24 integrated), and 36/36 inherited SHEET 161 network checks in an independent rerun. Whole historical regression chain not run.

SHEET 162 makes verified, signed S161 recovery pages commit in durable eight-row batches using the S160-compatible Merkle segment format, and reuses pinned mutual-TLS sockets via a bounded keep-alive agent.

## Modules

- `batch162.js`: **segment-bounded atomic durable batch**, index/frontier update, fail-closed orphan detection and two Ed25519 operator-signed orphan reconciliation.
- `node162.js`: real mTLS protected witness with inherited S161 certificate, session, signed page, and floor verification; new `/apply162` batch endpoint.
- `transport162.js`: reusable mTLS agent; CA and fingerprint verification, bounded sockets, request limits, transport counters.
- `catchup162.js`: signed witness recovery over persistent TLS; session cursor survives process failure.
- `unit162.js`: 19 storage and recovery checks.
- `gate162.js`: 24 network correctness checks, two legacy-vs-batched benchmarks and real restart test.
- `BENCHMARK-REPORT.md`: measured comparisons, reproducibility, and limitations.
- `KERNEL-ASCII.txt`: complete operation/failure process pipe.
- `index.html`: interactive SVG dashboard.
- `baseline161/`: preserved inherited release files (704 files; 703 match the original ZIP, plus a local release-build log).

## Quick verification

```bash
node unit162.js
node gate162.js
```

Run from the `sheet162` directory. Benchmark setup/seeding time is excluded from throughput. Test certificates are synthetic and temporary. The two A/B recovery paths use the same source history, but benchmark order is not randomized. Three source/target process roles and a simulated independent signer share one physical host. The complete historical inherited chain remains unverified this turn.

## Security boundaries

A signed page is fully verified before any batch mutation. A write never crosses the 256-record physical segment boundary within one batch. Segment-first/head-second fsync is recoverable, **not physically atomic**; a torn operation stays quarantined pending two independently signed operator approvals. Batching reduces fsync count, not cryptographic proof requirements.