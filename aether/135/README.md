# AETHER-135 — Unseen hidden physical reference faults (failed)
**FAIL. No phase credit. Phase VII remains 75%.**
The AETHER-134 policy was **frozen**, then tested on 50 unseen seeds × eight conditions × 32 ticks: 400 paired episodes, 12,800 decisions per policy. All **5,600/5,600** deterministic source-hash, event-chain, signed-packet and fail-closed checks passed, yet fixed recalibration authorized **800 unsafe ACT** and the adaptive policy authorized **1,250 unsafe ACT**.

Corrupted test conditions: hidden physical reference jumps, false drift rate, incorrect signed calibration bias, fraudulent signed ingress path, combined spoofing, and honest detectable anomalies. Clean and instrument replacement were controls. **A signed measurement can be accurately signed and physically false**. Recalibrating each tick does not solve a falsified reference's own output.

Frozen tested local source hash: `c633be2486fffb814f98e24975b78b40631e108dfc3915a854488b603f739710`. Repo scripts are separately authored and full GitHub-checkout replay unverified. Original results preserved, not overwritten. [AETHER-135B](../135b/) evaluates a stricter external-reference gate.