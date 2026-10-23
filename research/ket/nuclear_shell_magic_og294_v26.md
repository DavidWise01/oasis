# KET Experiment 26 — Independent nuclear shell-closure test

Date: 2026-10-23. Locally executed 10-case test with CSV and Python in conversation artifact ZIP.

The observed major nuclear magic numbers (separate proton Z and neutron N shell closures) are 2, 8, 20, 28, 50, 82, 126. Reference: LBNL https://www2.lbl.gov/nsd/education/ABC/wallchart/chapters/01/2.html and APS 2026 https://physics.aps.org/articles/v19/11 .

## Benchmarked cases
| Nuclide | Z | N | Both classical shells closed? | Status |
|---|---:|---:|---|---|
| He-4 | 2 | 2 | yes | stable |
| O-16 | 8 | 8 | yes | stable |
| Ca-40 | 20 | 20 | yes | stable |
| Ca-48 | 20 | 28 | yes | extremely long lived two-neutrino beta decay |
| Ni-56 | 28 | 28 | yes | radioactive |
| Ni-78 | 28 | 50 | yes | radioactive |
| Sn-132 | 50 | 82 | yes | radioactive |
| Pb-208 | 82 | 126 | yes | stable |
| Og-294 | 118 | 176 | no | alpha decay ~0.7 ms |
| Og-302 | 118 | 184 | no classical double closure | **hypothetical**; N184 proposed possible superheavy closure |

Local assertions PASS: 10 cases; A=Z+N; first eight double closures; Og294 118p + 176n; Og302 118p +184n; multiple magic nuclei are radioactive; Cf249 + Ca48 -> Og294 + 3n conservation.

**Caution:** This is a categorical consistency test, not a statistically fitted predictive nuclear stability model. No half-life extrapolation for unmade Og302, and N184 is theoretical rather than established universal magicity. Protons Z=118 are not classically magic.

KET typed closure: `[stable{(test-zone)}]` only preserves actually verified claims; separate electronic closure from nuclear closure and from chemical stability. Immutable 184/257 foundation unchanged.

Reproducible executable, CSV, JSON summary bundled separately in conversation.
