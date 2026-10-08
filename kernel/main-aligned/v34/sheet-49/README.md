# SHEET 49 — Blind internet chronology detection (v01)

Append-only experimental audit. Historical layer dates **were not used** to rank Exitron candidate points.

## Predeclared geometric sweep

- Reference baseline: `sheet-45/sheet45-exitron-v01.py` reversible 8+2 register transport.
- Index 0..192 maps to the **assumed**, not derived, 1832..2024 nominal year range.
- 16 Exitron transport ticks per indexed year; total 3,088 ticks, 61,760 lane-event updates.
- Each candidate score: `3 * crossings_while_open + crossings/4 + (before_worker_imbalance - after_worker_imbalance)/2**32`.
- Select top 17 scored years, breaking ties by earlier index. No history dates participate in scoring.
- Compare to 17 previously curated year anchors: 1832, 1844, 1866, 1876, 1901, 1945, 1969, 1973, 1983, 1991, 1995, 2001, 2006, 2011, 2016, 2019, 2024.
- 10,000 seeded random 17-point candidate sets as a null comparison for each tolerance.

## Measured result (local execution, 2026-10-08)

| Tolerance | Matched anchors | Random mean | Monte Carlo p (>= observed) |
|---|---:|---:|---:|
| Exact | 0 | 1.5096 | 1.0 |
| ±2 years | 5 | 6.0506 | 0.8212 |
| ±5 years | 9 | 10.5621 | 0.8468 |

Candidate years (rank order):
1838, 1856, 1972, 2018, 1975, 1884, 1948, 1924, 1902, 1906, 1999, 1930, 1929, 1841, 1954, 2017, 1951.

8/8 local computational assertions passed, including replay and exact reversal.

**Finding:** no evidence of better-than-random historical alignment from this selected transport mapping. The chronology's scale and 17-point target count are assumptions, not geometric deductions. Multiple comparison concerns remain if mappings or scores are tuned after observing history. No claim of physical tunneling, causation, or time dilation.

The intact preceding SHEET 42–48 versions are unchanged. Future versions must append rather than silently revise.
