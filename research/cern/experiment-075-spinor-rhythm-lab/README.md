# PRIM 075 — Agentic Spinor Rhythm Lab

**Open standalone interactive page:** [index.html](./index.html). Download the raw HTML and open it in a desktop browser; no libraries, API keys or server needed. Controls: Run/Pause, Step, Reset, Sweep, clock rate, pressure-drive amplitude, frequency multiplier and damping. Three autonomous local deterministic oscillator states, not language agents; no leader, votes or quorum.

Topology: `(((000)))` pinned shared reference, `1×4×4×1` center (16 logical cells), three orbital spinors spaced 120°, separate intrinsic spin offsets −15°, 0°, +15°, crossed inversion boundary `||\/|| = ||[;]||`.

Timing: `5557755777` sums to 60 (29+31). Three 20-unit sectors with 8 internal/12 external each; central cell pointer and beat synchronize every 240 units. The reference resonance curve uses the classical harmonic amplitude `A=F0/sqrt((k−mω²)²+(bω)²)` with normalized `m=k=1`. Canvas rendering and scan are symbolic/numerical, **not measured quantum physics**, and the reference sweep is not the Fourier response to the full 5/7 beat forcing.

Verification: `python test.py`; covers 240 ticks of 120° alignment, 16-cell closure, beat counts, directional nonaliasing and response sanity. No actual browser automation performed.
