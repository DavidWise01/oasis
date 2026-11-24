# AETHER-167 — Blind Independent Physical-Evidence Adjudication

**Phase XI Turn 7/8 · synthetic software readiness 87.5% · physical qualification 0% · operational HOLD.**

The exact local `experiment.py` source SHA-256 is `60401569f875a87de629b7233155288e3f0c1fdbad74a33b5f63d314d5a41b17`. It executed 25 seeds × eight scenarios × 20 ticks × two policies: **200 episodes / 4,000 decisions per policy**, **3,200/3,200 deterministic checks passed**, all decision traces hash-chained.

Signed-only comparator: **1,200 unsafe synthetic dry-run ACT**. Blind ancestry-gated controller: **zero unsafe**, preserving **2,800 safe synthetic dry-run ACT** (500 clean, 500 legitimate rotation). All real operational ACT remained HOLD.

Six synthetic faults: shared root ancestry, duplicate record masquerading as independent source, DUT-issued reference, conflicting simulated measurement, missing root and replayed nonce. The policy receives signed records only, not the scenario label or hidden truth; it applies one deterministic acceptance path without a vote.

**Three claimed roots are not authenticated independent evidence.** All signers and sources in this experiment were created by one test fixture. No physical witness, laboratory certificate or physical independent sensor was validated. [Physical register](physical_adjudication_register.json) retains null physical fields, and qualification remains 0%.

Locally executed complete source and 3,200 checks are in [local evidence archive](https://github.com/DavidWise01/oasis/tree/main/aether/167) **distributed separately as a conversation ZIP**, SHA-256 `552d51652950938655e096673ddac74f13142b86ed1f2f12ea755e4fa21b4aad`. The GitHub `experiment.py` is a distinct, condensed reproduction; identical checkout testing and latest live Pages deployment are unverified.

[Python demo](experiment.py) · [Results](results.csv) · [Manifest](manifest.json) · [Physical evidence register](physical_adjudication_register.json) · [Interactive lab](index.html) · [Phase XI tracker](../PHASE-XI-STATUS.md).

**Next AETHER-168:** final Phase XI software evidence freeze, without granting independent physical qualification.
