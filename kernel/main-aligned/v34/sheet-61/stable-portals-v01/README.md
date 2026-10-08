# SHEET 61 — Stable Portals -~~+ +~~-

Linear, append-only successor to SHEET 60; preserves the original 9-cell and 36-ambassador registry.

## Source-defined topology
- Nine permanently open logical portal nodes, one per cell of the 3×3 ⊞ windowed field.
- Every portal connects to each of the other eight: **36 undirected links**, or **72 directed paths**. This is not 81 distinct point-to-point external links (9×9 includes nine self-links).
- Each of nine cells retains four uniquely named ambassadors `C{1..9}-A{1..4}`.
- Retain exact notations `-~~+` ingress and `+~~-` egress; `~~` denotes symbolic tunnel.
- Source HTML is a *static drawing* with no portal flicker. The benchmark translates static openness to a software graph.

## Local executed preservation benchmark
12 cycles × 9 source cells × 4 source ambassadors × 8 other destinations = **3,456 records** and **72 exercised directed connections**.

18/18 assertions passed: nine stable portal states, all 36 unique ambassadors, complete connectivity, no self-links, unchanged source bytes and identity commitments, no duplicate delivery IDs, hash-chain integrity, deterministic replay, checkpoint restoration from tick 47 and tamper refusal, and correct logical-clock domain labels.

Ledger SHA-256 tip: `cc46ae510d0f068d77fc57d18bb6b193d775e219e94298c27582281b5f506f30`.

## Throughput negative control
The baseline records transfers instantly, without simulated service queues. A separate conservative test injects 32 packets per tick through capacity 16, accumulating peak backlog 1,728 after 108 ticks. All-open does **not** mean infinite channel capacity; a queued delivery engine is the logical next benchmark.

## Caveats
This is deterministic **symbolic information routing**, not evidence for literal stargates, time travel, or metaphysical realms. SHA-256 does not prove remote identity in an adversarial network. Checkpoint is in-memory, not durable crash recovery. The exact tested local executable is available as `/mnt/data/sheet61/benchmark.py`; this GitHub commit stores the audit/report and results, not the executable. Prior files remain unchanged.

## Next SHEET 62
Bounded all-to-all channel service with explicit acknowledgments, queue pressure, fairness and crash-safe retransmission.
