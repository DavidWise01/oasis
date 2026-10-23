# PRIM Experiment 022 — [(n())] delayed inference carrier

2026-10-23. Classical 17-oscillator [8×1×8] star, reciprocal coupling and delayed observed phases. Open nested container denotes finite first-order memory stages n=0,2,8, not physical Planck bubbles.

36 simulated trajectories, 2 seeds per 18 combinations: delays 0,.2,.5 sec; coupling 2 and 8 rad/s. Euler dt=.01 s, 12 sec runs, mean coherence over final 4 s. Natural frequencies mean 1 Hz SD 0.05 Hz.

At coupling=8, measured mean coherence:
delay=0: n0 .99925, n8 .99925
delay=.2: n0 .99903, n8 .99892
delay=.5: n0 .94032, n8 .89175.

**Important caveat:** n>0 adds low-pass lag AFTER the common pure delay; this is not a matched-total-delay or controlled-memory-benefit comparison. Eight stages make 0.5 sec example worse, not better. Short simulations, two seeds, no step-size sensitivity test, no quantum or Planck-bubble physics conclusions.

Reproducible simulation, results and README supplied in ChatGPT downloadable prim_exp022.zip. Next: equalized total delay and noisy phase measurements.
