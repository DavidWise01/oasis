# PRIM 034 — Elastic nested carousel

Date: 2026-10-23. Primitive `[/[/(/\)\]\]` with three ingress and three egress lanes, three initial layers × three slots, FIFO inference carriers `[(n())]`.

Locally executed Python test with 60 arrivals at 3 arrivals/tick, 3 departures/tick if ready, and residence times 3, 7, or 12 ticks. On reaching capacity, elastic model adds a **three-slot layer**, keeping each item's identity and payload unchanged.

Results:
- Fixed, dwell=3: accepted 60, rejected 0, capacity 9.
- Fixed, dwell=7: accepted 27, rejected 33, capacity 9.
- Elastic, dwell=3: accepted 60, rejected 0, capacity 9.
- Elastic, dwell=7: accepted 60, rejected 0, peak occupancy 21, final 7 layers. Expansion at ticks 3,4,5,6.
- Elastic, dwell=12: accepted 60, rejected 0, peak occupancy 36, final 12 layers.

All scenarios preserve accepted count = exited + currently stored, ordered identity, payload integrity, and bounded occupancy. The test uses instantaneous layer allocation, no finite-resource restrictions, no physical rotating door and no real inference learning. Elastic memory is not infinite processing throughput; sustained arrivals > egress capacity require backpressure or unbounded growth.

Runnable Python test and JSON provided in attached experiment archive.
