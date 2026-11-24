# AETHER-152 — Phase IX qualification evidence freeze

**Phase IX synthetic software protocol readiness CLOSED: 8/8 = 100%. Independently qualified physical evidence remains 0%.**

The exact local AETHER-152 integration imported only the *definitions* from an immutable frozen copy of the previously locally tested AETHER-151 Python controller (source SHA-256 `d4861612d1858ed333da70843251c24e7d40f3d14eede303afd97079f3f165a7`), preserving its authorization logic. It ran 25 new seeds × eight conditions × 20 ticks × two policies: **200 episodes per policy, 4,000 decisions per policy**. All **3,200/3,200 deterministic checks passed**.

The signed-only comparator authorized **1,200 unsafe dry-run ACT** in six constructed faults. The frozen blind-intake policy authorized **zero unsafe dry-run ACT** and preserved **2,800 safe dry-run ACT** (500/500 clean and 500/500 valid rotation). **Operational ACT=0** across all cases.

The seven accepted predecessor archives AETHER-145B through AETHER-151 were each checked for required source, manifest and checks entries; all ZIP CRCs validated. The [inventory](archive_inventory.csv) records observed archive and source SHA-256 hashes. Historical tests were inventoried, **not** comprehensively rerun. The AETHER-145 originally failed contract remains preserved in the 145 combined archive.

**Qualification status:** The bench truth is synthetic and the certificates and signing roots are mocks. There is no physical instrument measurement, no independent calibration traceability, no real same-path probe insertion, and no measured alarm reliability or uncertainty coverage. Therefore real-world qualification remains **0%**, and **all operational permissions HOLD**. 100% applies only to the eight planned synthetic protocol readiness bounds.

**Reproduction boundary:** GitHub's `experiment.py` is a separately authored checkout companion that imports GitHub `../151/experiment.py`, which differs from the locally frozen AETHER-151 source. The full exact local 152 source SHA-256 is `4c4e8f2bbb29346d9b8467462cb4b97035878713cd9f32358fa94477afe2ec73` and is packaged with the frozen predecessor source, 3,200 checks, all seed cases, sample traces, inventory, and manifest in the companion evidence ZIP. GitHub-checkout execution and live Pages deployment were not verified.

[Checkout companion](experiment.py) · [Local final results](results.csv) · [Final manifest](manifest.json) · [Archive hashes](archive_inventory.csv) · [Interactive Pages lab](index.html) · [Phase IX tracker](../PHASE-IX-STATUS.md).

**Next phase:** physical-data acquisition planning, not artificial advancement of hardware qualification. Begin with a real physical standard/fixture selection, calibration traceability check and direct raw capture under HOLD.
