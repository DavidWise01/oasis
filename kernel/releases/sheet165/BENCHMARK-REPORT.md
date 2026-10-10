# SHEET 165 — Measured Benchmark Summary

**Design:** 4 counterbalanced blocks × 8 factorial configurations (32 source-target trials), plus normal and higher latency holdouts (4 baseline/candidate pairs each; 16 more trials). Four blocks were run in isolated processes to avoid long-lived test-harness socket interference. Four signed-peers/target configuration? Actual 2 signed source witnesses and one target per trial, all over pinned local mTLS.

- Source: 384 certified records.
- Training: recover 96 records per trial.
- Holdout: 136 recovered records, crossing the 256-record physical segment boundary.
- Comparator: prefetch window 1; durable batch 8; persistent TLS.
- Candidate: window 4; durable batch 8; persistent TLS.
- Confidence method: 2,400 seeded paired-block percentile bootstrap draws of log throughput ratios, reported 95% interval.

| Phase | Geometric speedup | 95% bootstrap interval |
|---|---:|---:|
| Training, 4 paired blocks | 2.2456x | 1.7316x–2.7887x |
| Normal-latency holdout, 4 pairs | 2.4206x | 2.2895x–2.5341x |
| Higher-latency holdout, 4 pairs | 4.0367x | 2.7741x–7.5507x |

The high-latency comparison includes one baseline outlier at ~39.2 records/s; avoid extrapolating 4.0x beyond this test.

All 117 checks passed across six independently run suites, including local durable restart after a real kill and forced performance-watchdog downgrade using an intentionally unrealistic throughput floor. 14/14 Chromium dashboard checks passed.

**Limitations:** Four timing repetitions do not establish production-level confidence-interval coverage; one-host mTLS, synthetic delays, local fsync. SHA-256 integrity confirms packaging, not cross-host linearizability. Prior 775 release files preserved; historical test chain not rerun.

For the complete eight-row training table, all raw trials, source files, exact reports and confidence calculations, use the SHEET165 ZIP.
