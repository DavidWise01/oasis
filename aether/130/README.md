# AETHER-130 — Preserved failed rotation gate

Initial software evaluation on 400 paired synthetic episodes, 11,200 decisions per policy and 5,600 deterministic checks. **FAIL:** zero unsafe lineage-gated ACT, but valid certificate rotation incorrectly triggered HOLD because newly signed rotated certificates included their prior `signature` field as payload. Valid rotation safe ACT fell **719 → 319**, violating the predeclared nonregression gate. No phase credit.

See [AETHER-130B](../130b/) for corrected certificate serialization. Both are software simulations; no physical calibration or independent root-of-truth verification.
