# PRIM Experiment 017 — six-hop disturbance rejection

Date: 2026-10-23. Fixed phase step 0.3367 cycles/hop; regular correction −0.0101 cycles on hops 3 and 6. Inject +0.005 cycles at hop 4. Exact rational arithmetic (Python Fraction).

Six-hop end states: nominal 2.0000 cycles (0 drift); disturbed open-loop 2.0050 cycles (+0.005 cycles = 1.8° residual); disturbed with **perfectly known** −0.005 feedback at hop 6: 2.0000 cycles (0 residual). Thus nominal closure does not reject disturbances; ideal feedback corrects if disturbance is known. Feedback measurement noise/delay/instability not simulated. No claim about physical photons or CERN data.

Executable code and JSON data: ChatGPT downloadable prim_exp017.zip.