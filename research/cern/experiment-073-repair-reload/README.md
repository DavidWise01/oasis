# PRIM 073 — Repair under renewed pressure

Canonical `{{ (((000))) : Sp0 | Sp1 | Sp2 : ||\/|| : ||[;]|| }}`.

Repaired Sp0 starts at 0 with residual damage 0.015. Six pulse amplitudes (0,0.010,0.020,0.030,0.050,0.080 J) are simulated for 40 ticks. Failure threshold is 0.050 damage units; loaded increments are one-quarter of pulse energy, idle recovery is 0.005 per tick. Reservoir capacity 0.100 J; vent rate up to 0.020 J/tick. Repeat failure ticks: none, 14, 7, 5, 3, 2. 720 assertions pass, checking exact rational energy conservation and state. Once failed, subsequent energy is overflow, not silently discarded. These fatigue parameters are assumed, not measured physical laws. No leader, no quorum. Run `python test.py` for JSON and CSV results. Downloadable complete ZIP available in conversation.
