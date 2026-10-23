# Experiment 027 — PRIM three-axis sparse test

Frozen symbols:

- Primitive: `[-+{s1}{ns1}[(s3)]{ns2}{s2}-+]`
- Spatial: `{{ 1s8t1u8v 001w8x1y8z }}`
- Envelope: `[9^3 x 1^3 x 9^3]^3`

Formal product 150094635296999121, 729 address slots per mirrored domain per axis. **Formal configurations are not independent physically simulated cells.** Simulated 12000 trials at each of four shared noise fractions, using Gaussian sufficient statistics for 729 observations per side and axis. Results (rho: raw RMSE, corrected RMSE): 0: .000909862/.000922620; .1: .019240080/.000871766; .5: .042119112/.000665432; 1: .060211075/.000150819. Reference paths are assumed to measure common disturbance independently of true phase; this assumption enables excellent rejection and is not proved by geometric symmetry. Reflection and address-reversal invariance checks passed. Exact arithmetic six-hop closure passed. No dynamical oscillator synchronization, physical photon data, or literal infinite nesting simulated.

Full simulation and JSON produced as `prim_exp027` in the ChatGPT session.
