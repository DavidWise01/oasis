# AETHER-127B — Failed random-only coverage, preserved

All **6,720 synthetic deterministic checks** passed and modeled unsafe authorizations fell from **665 to 0**, but clean safe ACT dropped **1,918 → 1,588**. Pure random sampling of 88 of 101 possible input counts sometimes leaves points more than one unit from any calibration probe, forcing HOLD despite a healthy instrument.

**FAILED clean nonregression gate. No phase credit.** The corrected [AETHER-127C](../127c/) guarantees radius-1 coverage before it authorizes ACT.

The test assumes hidden same-path challenge inputs and trusted physical behavior; it is not a general proof of sensor integrity.
