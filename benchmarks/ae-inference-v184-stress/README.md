# v184 scale-to-failure benchmark

This harness leaves sealed v184 unchanged and increases problem size until a
single case crosses an 8-second soft stop.

Series:
- two-stage unary propagation
- two-premise keyed join
- transitive closure

The goal is to locate the current exhaustive matcher's scaling knee, not to
claim hardware-independent throughput.
