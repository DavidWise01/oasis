# N184 v6.1 — Browser lattice integrity evidence

**Reported:** 2026-10-17
**Evidence:** User-supplied browser test output from the [v5.9 certification console](../two-tab-certification-v59/).
**Attribution:** First-party operator report; not independently reproduced by the assistant.

## Verbatim output

```text
38,400 lattice reversible + unique: PASS
Strong scale equality: PASS
X zero sum: PASS
```

## Findings

- **PASS (user-reported):** 2,400 lattice addresses × 16 nibble states = 38,400 reversible, unique address/state mappings.
- **PASS (user-reported):** box/toroid strong convergence `(6 × 6)^6 = 2,176,782,336`.
- **PASS (user-reported):** X offsets `a(-2,+3), b(-3,+2), c(+2,-3), d(+3,-2)` sum to `(0,0)`.

## Certification register

| Gate | Status |
| --- | --- |
| Two-tab CAS race, one commit, one stale rejection | PASS — user-reported |
| Abort leaves database unchanged | PASS — user-reported |
| 38,400 unique reversible mappings | PASS — user-reported |
| Strong-scale equality and X zero sum | PASS — user-reported |
| Persisted checkpoint verified after an actual page refresh | PENDING |

**Freeze decision:** HOLD until reload inspection evidence. External crash / power-loss durability not established. The frozen symbolic geometry is unchanged and no physical tunneling claim is made.
