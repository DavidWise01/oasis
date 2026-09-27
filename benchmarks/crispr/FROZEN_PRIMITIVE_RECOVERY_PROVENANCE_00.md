# Frozen Primitive Recovery + Provenance 00

Status: **PASS**

Recovery rule:

```text
matching checkpoint copies >= 3
AND
independent ancestry roots >= 3
AND
unique source identities >= 3
```

Results:

```text
3 canonical / 3 roots          -> RECOVER
3 forged / 1 root              -> REJECT
3 forged / 2 roots             -> REJECT
local corrupt + valid 3 roots  -> RECOVER CANONICAL
3 forged / 3 real roots        -> FALSE RECOVERY threshold reached

RESULT = 0e
```

This closes the nominal-vote spoof from the prior recovery test: three matching names or source IDs are insufficient unless their ancestry is independently rooted.

The remaining hard boundary is coordinated compromise of three genuinely independent provenance roots.
