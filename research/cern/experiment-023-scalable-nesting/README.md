# Experiment 023 — PRIM scalable nesting

Two executed numerical tests, 2026-10-23.

**A: virtual nesting (depth 0–1024)** 17-oscillator [8×1×8] simulation. R=0.9993162441 at all 12 tested virtual depths, because depth does not change dynamical equations or observations. This is *by construction*, not evidence of physically simulated 1024-layer nesting.

**B: independently noisy observation replicas n=1–1024**. Circular mean of n independent noise-corrupted observations at nominal fixed 0.02 s latency; 13,600 phase samples. RMSE decreases from 0.0597197 to 0.00187709 rad (31.8×). This is expected ~1/sqrt(n) averaging. Constant sensing latency is assumed, not experimentally demonstrated. No correlated noise or physical quantum-photon modeling.

Code and JSON are provided in ChatGPT file `prim_exp023.zip`. All limitations and run instructions documented there. Next: implement actual hierarchical aggregation and common-mode noise controls.