# PRIM 024: [(n())] hierarchical phase estimation

Date 2026-10-23. Binary tree with 2^n independent leaf slots, actual pairwise aggregation, n=0..10, 4096 trials per configuration, rho=0,.01,.1,.5,1 correlated Gaussian phase observation noise, sigma=0.06 rad. All 55 cases within 5.5% of predicted RMSE = sigma sqrt(rho+(1-rho)/2^n).

At 1024 leaves: RMSE ~0.001845 rad (rho=0), ~0.018890 rad (rho=.1), ~0.059611 rad (rho=1). Aggregation needs 2046 child messages per trial at depth ten. Scaling benefit requires independent information; common noise yields an error floor.

No dynamics, delay, noise wraparound, or experimental photon behavior tested. This is a numerical estimator rather than physical infinitely nested Planck bubbles.

Full tested files in ChatGPT downloadable archive prim_exp024.zip.