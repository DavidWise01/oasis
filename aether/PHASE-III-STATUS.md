# AETHER Phase III — Live Tracker

**1 / 8 approved · 12.5% complete · Current: AETHER-104 PASS.**

Phase II closed at [AETHER-103](103/) and remains frozen at 100%. This is a separate phase addressing evidence-root lineage, adversarial witnesses and Byzantine-style failures.

| Turn | Bound | State | Completion |
|---|---|---|---:|
| 1 | **104 — Root lineage deduplication** | **ACCEPTED** | **12.5%** |
| 2 | 105 — Forged/shared ancestry | Next | 12.5% |
| 3 | 106 — Conflicting source assertions | Not started | 12.5% |
| 4 | 107 — Fault-aware quorum | Not started | 12.5% |
| 5 | 108 — Delayed and reordered evidence | Not started | 12.5% |
| 6 | 109 — Coordinated dishonest roots | Not started | 12.5% |
| 7 | 110 — Byzantine stress and recovery | Not started | 12.5% |
| 8 | 111 — Integration and phase freeze | Not started | 12.5% |

## AETHER-104 acceptance evidence

- **6,000** deterministic synthetic cases across three declared scenarios.
- Naive message-weighted strategy incorrect: **2,472** cases.
- Root-aware strategy incorrect: **153** cases, and abstained (HOLD) **618** times.
- All three declared gates passed, including never authorizing from only one root and eliminating incorrect classifications from four duplicate copies of one corrupted ancestor in the cloned-corrupt cases.
- **Limit:** ancestry metadata is trusted in this bound; forged root identities are left to AETHER-105. No proof of real-world source authenticity.
- [Source and outcomes](104/). GitHub Pages is a separate deployment verification.

## Hegemonic/diodic invariant

One canonical controller uses forward-only evidence; quorum is a condition on admissible evidence **not** a competing decision governor. Provenance roots do not vote for governance or change historical logs. HOLD is required when independent support is insufficient.

Percent = 100 × accepted bounds / 8. Failed bounds stay unfinished; archive the failed case without credit. Close early only if a genuinely new primitive beyond this phase is required; never call early closure 100%.

`{24/[2]/[4]/(3)/(3)/(1)/(1)} · {{i}} · .dlw`
