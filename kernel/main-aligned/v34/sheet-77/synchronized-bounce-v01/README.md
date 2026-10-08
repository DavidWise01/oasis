# SHEET 77 — Synchronized Plank Bouncer

Append-only successor to SHEET76. Four visual oscillator shells run at periods 256/64/16/4 ticks. One 60-bit wave register rotates +15 and inverts at each discrete phase step; it repeats every four ticks. A binary latch starts at 1 and toggles on master-shell turnaround events at ticks 64 and 192, yielding `1 → 0 → 1`.

## Verified result

`python benchmark.py` passes **24/24** checks locally. The first recurrence of the combined logical state (four integer phases, four directions, binary latch, entire 60-bit wave, 416-item registry definition, geometry metadata and sqrt(1.25) metadata) occurs at **tick 256**, and again at 512. Full state hash matches. The floating-point sampled shell radii also match at 256 to tolerance.

The implementation uses an explicitly selected common master clock: synchronization is engineered, not inferred from physics. Only the outer shell triggers the latch; inner-shell turning points are not all used as logical flips. This does not prove a gravitationally coupled orbit, natural Planck physics, or thermodynamic homeostasis. Earlier files not changed.

Run `python benchmark.py > results.json`.
