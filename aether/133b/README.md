# AETHER-133B — Same-path acquisition binding

**Accepted constrained synthetic result:** 40 seeds × 10 path/receipt scenarios × 24 ticks = 400 paired episodes and 9,600 decisions per policy. **5,600/5,600 deterministic checks passed**. The signed-only calibration comparator authorized **3,200 unsafe ACT** while the protected ingress-bound controller authorized **0**; both retained **6,400 safe ACT** in these seeded examples.

A signed calibration certificate is not enough. A separate *trusted* ingress signer binds challenge insertion, calibration, risk measurement, protected port, routing/path identity, insertion nonce, device generation, and monotonic acquisition counter to **one tick**. A mismatch or missing receipt causes HOLD. In a legitimate instrument rekey the new generation is consistently bound and clean ACT remains 960/960.

The **failed AETHER-133** first pass had 240 failing signature-integrity checks because the synthetic mutation helper re-signed packets without removing their prior `mac` field. AETHER-133B normalizes the signing payload before creating a fresh MAC. Both complete source snapshots and corresponding trace/check CSVs remain archived.

**Physical boundary:** The ingress signer, physical route observations, reference path and nonce integrity are all simulated and trusted by construction. The receipt's claim of same-path routing is not an independently measured physical fact; signatures cannot establish real route topology or protect against key compromise. No physical validation was performed. The code/CSV archive is imported from the **locally executed source snapshots** and the core Python code was published without changing its logic.

[Python experiment](experiment.py) · [Seed results](seed_results.csv) · [5,600 checks](checks.csv) · [Trace sample](trace_samples.csv) · [Aggregate results](results.csv) · [Manifest](manifest.json) · [Interactive HTML](index.html).

**Phase VII progress: 5/8 accepted = 62.5%, under bounded synthetic software gates.**
