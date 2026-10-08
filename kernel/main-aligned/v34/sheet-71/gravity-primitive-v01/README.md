# SHEET 71 — Gravity Primitive (-g / 0g / +g)

Append-only successor of SHEET70, preserving earlier kernels. Source: user-provided compiled React HTML with labels **EXPANSION (-g)**, **MAX (0g)** and **COMPRESSION (+g)**. Its toy radial equation is `a'' = -GM/a^2 + lambda*a`. Interpret phase from radial **velocity**, not from acceleration: outward / zero / inward.

The artwork retains 300 strong, 100 medium, 16 weak = 416 symbolic particle IDs. Source's '0g' label does not imply a zero gravitational field. Parameters and physical units are unspecified; this is a toy ODE, not established Friedmann gravity or actual time travel.

## Local verification

The standalone local Python benchmark uses velocity-Verlet, mu=1, lambda=.04, dt=.002, initial radius=4, outward speed=.8. It ran 4,180 steps to radius >20, reversed to near its original radius/velocity (error 3.29e-14 / 9.10e-15), with energy-like invariant drift 2.99e-7. 416 source-aligned IDs remained byte-preserved; 16/16 checks passed. Inward-velocity initial control -0.8 fell into the model's radius-zero singularity: a genuine limitation recorded rather than hidden.

The three labels are classified, but the forward trajectory itself observed expansion only. Thus **cyclic gravity has not been demonstrated**, and a turnaround must not be invented to match the illustration. Keep `9/6/1` and `sqrt(1.25)` homeostatic occupancy as independent queue-control primitives; no gravity-induced physical time dilation is asserted.

Local executable + JSON + audit are available in this conversation's ZIP. GitHub stores this report and results summary; exact executable CI replay is still outstanding.
