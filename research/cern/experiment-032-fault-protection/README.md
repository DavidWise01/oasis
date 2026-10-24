# Experiment 032 — Tesseract fault protection

2026-10-23. Topology: eight separate T nodes in a weak non-contact bleed ring, central mediator H, held incubator I. 10 nodes/17 undirected links. Couplings: hold=1.0, portal=0.5, bleed=0.1 (rad/s).

32 classical oscillator runs (fault on/off, link-delay jitter on/off, causal inference carrier on/off, four seeds) over 32 modeled seconds (dt=0.02 s). T0 receives +0.9 rad kick at 10 seconds and telemetry receives +1.6 rad error from 11.2 to 11.34 seconds. Baseline portal and bleed delays are .08 and .04 s. With jitter, Gaussian SD=.055 s truncated at zero. Inference pocket `()` clips observed phase innovation at ±.12 rad before a 0.35 smoothing update.

Mean peak incubator-to-hub phase error during disturbance: direct no-jitter .0611318, `()` carrier .0476411 rad (~22% reduction); direct with jitter .0607741, carrier with jitter .0475816. Mean final network coherence ~.9997729 in all tested configurations. Carrier benefit is transient, not discernible in final coherence. Four seeded trials per condition are too few for general reliability claims. No learning, optical photon interaction, or literal 4D geometry simulated.

Full tested Python and JSON provided in downloadable conversation archive `prim_exp032.zip`. Next: matched-noise paired trials, stronger and multiple faults, estimator failure modes and time-step convergence.