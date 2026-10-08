# SHEET 57 — Durable Temporal Memory

Append-only successor to SHEET 56. The historical versions remain unchanged.

## Scope
Symbolic domains: HEAVEN ×3, EARTH ×2, HELL ×1 (logical clocks; **not** real temporal travel).

The local executable uses the unmodified SHEET 56 logic and its SHEET 53 reversible operator, adds **two file-backed checkpoint generations**, writes to staging files using `flush + fsync`, promotes them with `os.replace`, and synchronizes the directory. Recovery verifies the SHA-256 of the checkpoint payload and selects the newest valid sequence.

## 2026-10-08 local test
17/17 checks passed in ~0.97 s. The reference run contained 8,640 messages, 25,920 hop records, zero duplicate deliveries, and exact register reversal. After generation 2 was deliberately truncated, recovery rejected it, fell back to verified generation 1, replayed, and produced the same final-state digest `da548cdcd99e6050e7549ad4912a1f8cdcc9c85e51428acdb25dcec8d979a022` and the same terminal logical tick 4321.

Other negative controls: corrupted both generations -> recovery refusal; uncommitted `.pending` checkpoint ignored; metadata tampering rejected.

## Limits
- Simulated checkpoint truncation, not an actual power interruption.
- In-memory output sink and replay, **not** an external transactional delivery sink. Older checkpoint replay could resend externally delivered effects.
- SHA-256 is not a digital signature or authenticated identity proof.
- The model does not demonstrate physics, quantum tunneling, time dilation, or a physical Stargate.

The tested standalone local artifacts: `/mnt/data/sheet57/benchmark.py`, `sheet56_baseline.py`, `sheet53_baseline.py`, and `results.json`. GitHub contains the audit/results; executable replay in GitHub has not yet been performed.

Next target: SHEET 58 — persisted sink acknowledgements and crash-atomic exactly-once **effect** semantics.
