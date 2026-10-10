# SHEET 165 — Counterbalanced Adaptive Recovery

Status: **0e / PASS**. 117 individual assertions passed across six separately executed suites (repeated unit assertions included); Chromium dashboard 14/14.

Upgrades the SHEET 164 mTLS Merkle recovery system with:
- Eight policy configurations from prefetch {1,4}, batch {4,8}, and TLS {fresh,reused}.
- Four seeded, counterbalanced factorial blocks with fresh persisted target journals.
- Paired-block bootstrap confidence intervals on log throughput ratios (2,400 replicates).
- Two disjoint, four-pair holdout benchmarks: normal and higher injected latency.
- Confidence-gated workload choice: fall back to the verified 1/8/reused baseline if the holdout 95% lower bound does not exceed 1.05x.
- Runtime performance-only downgrade after a durable commit and authenticated cursor restart. Authentication, quorum, Merkle and floor failures are **not** retried under fallback.
- Actual killed-process crash test and no duplicate durable writes.

**Measured:** Candidate 4/8/reused. Normal holdout 2.42x paired geometric mean, bootstrap interval 2.29–2.53x. High-latency holdout 4.04x interval 2.77–7.55x, with an unusual slow baseline outlier.

**Caveats:** All measurements on one physical host, just four paired repetitions, artificial latency, no independently hosted consensus proof. Full historical regression chain was not rerun. Published predecessor ZIP preserved exactly (775 files). SHA-256-manifested complete executable harness and frozen history are in the full SHEET165 ZIP attached in conversation.

Run from complete ZIP: `cd sheet165 && bash run-new.sh`.
