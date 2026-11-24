# AETHER-146 — Quarantined calibration-certificate intake

**Phase IX Turn 2/8; software protocol readiness 25%; empirical physical qualification 0%.**

The exact locally executed 146 experiment ran 30 seeds × 8 conditions × 20 ticks = **240 episodes per policy** and **4,800 decisions per policy**. **3,840/3,840** deterministic checks passed. Signed-only admission permitted **1,440 unsafe dry-run ACT**; quarantined intake permitted **zero** and preserved **3,360 safe dry-run ACT**. Clean and valid-rotation cases each retained **600/600** safe acts.

Cases: clean; valid device rotation; absent certificate; expired certificate; mismatched reference serial; altered raw-data SHA-256; DUT self-issued reference; and acquisition challenge mismatch. Rejected evidence is quarantined (no inferred repair). **All physical operational ACT remain HOLD.**

**Important limitation:** This is a software intake contract, not real calibration assessment. The external issuer is an assumed mock HMAC root, declared accreditation is a string, and raw values are generated from synthetic truth. A passing software certificate **cannot** certify its own physical provenance or validate metrological accuracy.

**Reproducibility:** The GitHub `experiment.py` is a standalone synthetic reproducer, separately authored from the full locally tested experiment. The `results.csv` and `manifest.json` report local execution. Matching GitHub-checkout reproduction and live GitHub Pages deployment are unverified. The companion ZIP contains exact locally executed Python, all 3,840 checks, seed cases, trace samples and result manifest.

[Python reproducer](experiment.py) · [Results](results.csv) · [Manifest](manifest.json) · [Interactive lab](index.html) · [Phase IX tracker](../PHASE-IX-STATUS.md).
