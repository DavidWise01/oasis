# Frozen Primitive Calibration-Head Pinning / Checkpoint Provenance 00

Status: **PASS**

Tests: **24 / 24 PASS**

This plane starts from the prior failure:

```text
C0 -> C1
       ^
       current head could be changed
       without breaking ancestry
```

Repair:

```text
C0 -> C1
       |
       +--> P0
       +--> P1
       +--> P2
```

The current head is now externally pinned.

Battery covered:
- current-head tamper detection
- 2-of-3 and 3-of-3 pin thresholds
- correlated pin roots
- epoch rotation
- stale-head replay
- same-epoch equivocation
- pinset transparency
- independent observers of the pinset
- checkpoint freshness
- 10,000 pinset mutations
- 10,000 current-head mutations

Progression:
```text
mutate current calibration head
    -> pins reject it

compromise one pin
    -> insufficient

compromise two independent pins @ 2-of-3
    -> boundary

raise threshold to 3-of-3
    -> blocks until all 3 pins change

rewrite pinset transparency too
    -> observers reject it

rewrite observer threshold too
    -> checkpoint plane exhausted
```

Current failure boundary:
```text
calibration head
+ threshold pin witnesses
+ pinset transparency
+ threshold transparency observers
all coherently rewritten
        ↓
no independent checkpoint reference remains
```

RESULT = 0e
