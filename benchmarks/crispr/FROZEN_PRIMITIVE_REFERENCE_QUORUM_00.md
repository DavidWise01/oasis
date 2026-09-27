# Frozen Primitive Reference-Corruption Quorum 00

Status: **PASS**

Witness set (5):
- light value
- shadow value
- canonical mapping
- frozen shell
- decision rule

## Thresholds

| Quorum | Minimum compromised witnesses for false pass | Tolerated compromised witnesses |
|---|---:|---:|
| 3-of-5 | 3 | 2 |
| 4-of-5 | 4 | 3 |
| 5-of-5 | 5 | 4 |

Explicit `3 witnesses / 2 agree / 1 decision` triplet:
- minimum compromised witnesses for false pass: **2**
- tolerates: **1** compromised witness

```text
3-of-5 baseline

0 corrupt -> PASS-safe
1 corrupt -> PASS-safe
2 corrupt -> PASS-safe
3 corrupt -> FALSE PASS becomes possible
4 corrupt -> FALSE PASS possible
5 corrupt -> FALSE PASS possible

threshold = 3 coordinated corruptions
```

The result is purely a validator/quorum property: it does not establish biological correctness.
