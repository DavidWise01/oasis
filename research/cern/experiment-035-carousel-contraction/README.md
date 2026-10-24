# PRIM 035 — Elastic contraction checkpoint

Executed 5 FIFO routing scenarios, 60 attempted observations each. Three ingress and three egress channels; baseline 9 storage positions (three layers). Reclaim only wholly unoccupied three-slot storage layers; no accepted inference record is discarded, duplicated, or reordered.

| Dwell (ticks) | Accepted | Rejected | Peak occupied | Expansion | Contraction | Final layers |
|---|---:|---:|---:|---:|---:|---:|
|3 elastic|60|0|9|0|0|3|
|7 elastic|60|0|21|4|4|3|
|12 elastic|60|0|36|9|9|3|
|20 elastic|60|0|60|17|17|3|
|7 fixed|27|33|9|0|0|3|

Tested conservation and FIFO identity/payload retention. Assumptions: instantaneous layer allocation/reclamation and limited-duration arrivals; not a proof of physical infinite capacity or quantum behavior. Run `python test.py`. Full event trace available in conversation ZIP `prim_exp035.zip`.
