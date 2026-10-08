# SHEET 78 — Independent clocks, synchronization negative control

Append-only successor to SHEET77; no earlier sheets modified.

Test the C60 six-arity 60/15/3/1/1 register (shift +15 plus XOR1), 416 source-defined registry entries, four symbolic nested oscillator phase clocks and independent binary latch. Unlike SHEET77, there is **no common 256-tick clock**. Instead, choose deliberately separate integer periods 251, 67, 17, 5 (oscillators), 4 (60-position register), and 263 (binary latch).

The local execution checked **100,000 ticks**, observed **zero exact combined-state recurrences**, and passed **16/16 checks**. Partial agreement at ticks such as 1,004 is **not** full closure. The least common multiple is **1,503,776,140 ticks**: `state(1503776140)==state(0)` was verified directly using exact modular arithmetic, without iterating through the entire interval.

This does **not** prove natural emergent synchronization or that physical clock frequencies must be prime. The values were chosen for a deterministic negative control. Replacing deliberately chosen periods with physical parameters would be a different test. The binary clock and C60 register retain their original identities and metadata.

Run `python benchmark.py > results.json`. Source was copied from the locally executed test. Prior sheets remain append-only.
