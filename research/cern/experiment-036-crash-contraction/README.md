# PRIM Experiment 036 — Interrupted contraction

36 restart scenarios passed with JSON-serialized checkpoint reload. 3 dwell times (7,12,20 ticks) x 6 crash ticks (20,21,22,27,31,39) x 2 restart points (after contraction intent preparation, after commit).

Each case admitted 60 unique open inference records and exited all 60 in order, no duplicate/lost accepted records, returned to baseline 3 storage layers.

Important limitation: simulated JSON rehydration, not real durable storage, process kill, torn disk writes, or external exactly-once acknowledgment. Next boundary: append-only journal, commit/ack separation and torn-write recovery.

ASCII:
```
3 INGRESS -> [nested ()] -> PREPARE SHRINK
                              |
                         RESTART STATE
                          /        \
                       EMPTY      BUSY
                         |          |
                       SHRINK     RETAIN
                          \        /
                            3 EGRESS
```

Full runnable Python and JSON results included in conversation ZIP prim_exp036.zip.
