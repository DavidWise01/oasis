# AETHER-130B — Calibration ancestry and traceability

**PASS, synthetic software-only.** 10 scenarios × 40 new seeds = 400 paired episodes; 28 decision ticks each = **11,200 decisions per policy**, 5,600/5,600 deterministic acceptance checks. Signed-only gate **3,200 unsafe ACT** in simulated falsified-reference scenarios; lineage gate **0**. Legitimate safe ACT **7,597/7,597** preserved. Valid certificate rotation safe ACT **719/719**.

Controller checks the signed root→lab→instrument chain; a declared root distinct from the risk ancestry, cycle/missing parent rejection, matching device and reference serial, bounded certificate validity, structured uncertainty components and the original current signed risk bound. Invalid ancestry yields **HOLD**; only one central governing controller selects action.

**Critical limitations:** "independent_from" is a *declaration* encoded in a signed synthetic certificate, not evidence of true physical independence. Physical traceability requires independent calibration records and actual instrument readings. The additive uncertainty budget neglects correlation. The simulated dishonest reference can be detected only because its supporting chain is synthetically invalid. A coherent but fraudulent signed chain would bypass this software gate. No field safety proof, no witness voting and no Byzantine/quorum architecture.

The failed [AETHER-130](../130/) is archived. Run `python experiment.py` (NumPy, SciPy) to reproduce all checks, summary tables and audit traces.
