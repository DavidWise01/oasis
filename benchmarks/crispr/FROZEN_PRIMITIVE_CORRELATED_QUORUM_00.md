# Frozen Primitive Correlated Quorum 00

Status: **PASS**

Quorum: **3-of-5**

This test asks how many independent source failures are required to create a false pass when witness channels share upstream state.

| Scenario | Independent sources | Minimum failed sources for false pass |
|---|---:|---:|
| Independent witnesses | 5 | 3 |
| Light + shadow share source | 4 | 2 |
| Light + shadow + map share source | 3 | 1 |
| Map + shell + rule share source | 3 | 1 |
| Two correlated pairs + one independent | 3 | 2 |

Key result:

```text
nominal 3-of-5 with true independence:
3 source failures required

3 witnesses sharing one bad source:
1 source failure can produce 3 wrong votes

quorum survives only if witness provenance is independent
```

Therefore, vote count alone is not enough. The validator must also track source independence / provenance before treating votes as separate witnesses.

RESULT = 0e
