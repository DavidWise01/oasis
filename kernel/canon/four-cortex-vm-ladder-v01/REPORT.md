# Four-Cortex VM Ladder Benchmark

Status: **PASS**

Tests: **11/11 passed**

```text
C1 IPv4
  ↓  1x1 {{i}} 1x1
C2 IPv6
  ↓  1x1 {{i}} 1x1
C3 quasi-q
  ↓  1x1 {{i}} 1x1
C4 quantum
```

- PASS — `boundary_shape`: 1x1 {{i}} 1x1
- PASS — `four_cortex_order`: C1→C2→C3→C4
- PASS — `identity_preserved_full_ascent`: {{i}} unchanged across all 3 VM boundaries
- PASS — `local_payload_mutates`: 5/5 distinct payload states
- PASS — `cortex_isolation`: no local-state keys shared across cortexes
- PASS — `boundary_corruption_detection`: 3/3 corrupt carriers rejected
- PASS — `frame_invariant`: all boundaries remain 1x1 | {{i}} | 1x1
- PASS — `round_trip_identity`: C1→C2→C3→C4→C3→C2→C1 preserves {{i}}
- PASS — `stress_100k_identity`: 100,000 transforms; identity failures=0
- PASS — `stress_50k_corruption`: 50,000 corruptions; undetected=0
- PASS — `deterministic_replay`: same seed reproduces identical trace

The benchmark validates the symbolic VM architecture only; it does not establish literal protocol/quantum equivalence.
