# SHEET 54 — End-to-end bounded retention

Linear append-only successor: SHEET 52 -> SHEET 53 -> **SHEET 54**.

## Tested model

Reuse SHEET 53's exact 10-word reversible operator. Synthetic offered load: 720 ticks x 12 offers = 8,640; service 2/tick. Engine-owned storage limits: source 128, center 64, quarantine 128. When all local capacities are exhausted, do not silently accept tokens: classify them as **deferred** (external sender retains ownership; retry not yet implemented), or **rejected** (explicit refusal). Both modes keep an append-only hash-linked delivery ledger and verify exact inverse of admitted register updates.

## Local executable test, 2026-10-08

| Metric | Defer | Reject |
|---|---:|---:|
| Offered | 8,640 | 8,640 |
| Accepted and delivered | 1,756 | 1,756 |
| Deferred externally | 6,884 | 0 |
| Explicitly rejected | 0 | 6,884 |
| Internal accepted lost | 0 | 0 |
| Peak source | 126 | 126 |
| Peak center | 62 | 62 |
| Peak quarantine | 128 | 128 |
| Last drain tick | 877 | 877 |
| Exact reversal | PASS | PASS |
| Provenance and tampering | PASS | PASS |

16/16 assertions passed in local execution. Both policies produced identical final register digest `b94555651e37217725a13c22fe3bac621fec60e1e8c5422327786593b770d5d3`. Ledger tip `ba244ba0fcf46dc024187990d3c0973d60ab8fd71fd3a25f0c05bb6be5586739`.

**Limits:** No automatic retry of 6,884 deferred tokens, and end-to-end retention of *all offered* tokens is **not** claimed. The input generator is synthetic. These are software-level audit results, not a particle/quantum model. The executable and complete results were generated locally, but are not included in this commit; replay in GitHub CI is outstanding.

No previous SHEET files modified.
