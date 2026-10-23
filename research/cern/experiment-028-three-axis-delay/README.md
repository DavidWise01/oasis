# PRIM Experiment 028 — delayed three-axis core

Date: 2026-10-23. Sparse 7-oscillator star, representing three mirrored axes and one common center in `[9^3 x 1^3 x 9^3]^3`. Preserves spatial token `{{ 1s8t1u8v 001w8x1y8z }}` without mapping addresses to physical distances.

Python simulated 48 trajectories, 8 random seeds per delay, via Euler integration dt=0.002 s over 24 s. Natural-frequency SD=0.04 Hz, bidirectional coupling K=5 rad/s; same propagation delay on every spoke within each run.

Delay (s) / mean phase coherence / runs above R>0.95:
- 0.00 / 0.998785 / 8 of 8
- 0.02 / 0.998764 / 8 of 8
- 0.05 / 0.998691 / 8 of 8
- 0.10 / 0.998506 / 8 of 8
- 0.20 / 0.997981 / 8 of 8
- 0.35 / 0.819596 / 3 of 8

The result shows decreasing phase coherence with delay in this toy classical model; no universal delay limit, physical photon synchronization, adaptive inference or Planck-scale physics established. In particular, this preliminary test uses identical delays along all axes, not spatially unequal propagation. Next test: unequal link delays, time-step convergence and genuine frequency-lock diagnostics. Runnable test.py and results.json delivered in conversation archive prim_exp028.zip.