# AETHER-159 — Blind combined-fault intake

**Phase X Turn 7/8: synthetic setup readiness 87.5%, physical qualification 0%, operational authority HOLD.**

Exact locally executed experiment: 25 seeds × eight cases × 20 ticks × two policies, **3,200/3,200 checks PASS**. Signed-only comparator admitted **1,200 unsafe dry-run ACT** and blind-intake gate admitted **0**, retaining **2,800 safe dry-run ACT**. Clean and legitimate rotation both retained 500/500.

Six adversarial combinations: capture loss + alarm suppression; issuer mismatch + route bypass; reference counter replay + delayed alarm; coherent false readings shared by mock reference and bench while raw bytes contradict; expired certificate + suppressed alarm; and signed false reference value. Blind authorization saw signed records and raw byte capture only, not scenario names or test truth. Scoring was after decisions.

**Limits:** The supposedly independent reference/bench receipts were synthesized by the same fixture. Synthetic combinatorial faults cannot prove detection of unknown physical faults or real metrological independence. No physical data/issuer was authenticated; [physical intake register](physical_blind_intake_register.json) remains null. Real operational ACT = 0.

Exact local executed Python SHA-256: `c02f6aa6bf43b46b0b0e92fa5b604c05392c6a237b7d0cde3c971a9a13cb4f56`. The exact local full source, all checks, seed results, SHA-256 traces, manifest and uncommissioned register are in the attached ZIP. GitHub `experiment.py` is a separately authored smaller reproducer; byte-identical checkout replay and live Pages deployment are unverified.

[Python](experiment.py) · [Results](results.csv) · [Manifest](manifest.json) · [Register](physical_blind_intake_register.json) · [Lab](index.html) · [Phase X tracker](../PHASE-X-STATUS.md).

**Next AETHER-160:** Phase X final decision freeze, 100% synthetic software protocol if integrative audits pass, 0% physical qualification in the absence of authentic measurements.
