# AETHER-147 — Immutable raw acquisition and provenance requirements

**Phase IX 3/8 · synthetic software protocol readiness 37.5% · physical qualification 0%.**

A locally executed complete experiment tested **30 seeds × eight acquisition scenarios × 20 ticks**, giving **240 episodes / 4,800 decisions per policy** and **3,840/3,840 deterministic checks**. Signed-only acceptance incorrectly permitted **1,440 unsafe dry-run ACT**, compared with **zero** for the raw-lineage gate. **3,360 safe dry-run ACT** were retained (600 clean and 600 legitimate rotation). All operational decisions remained HOLD.

The model preserves an original byte representation and hashes it before controlled transformation. Each receipt binds generation, serial, tick, nonce, ordered sample indices, deterministic derivation algorithm and stated uncertainty. The mock original-to-derived lineage fails closed for missing bytes, altered bytes, reordered samples, dropped samples, a forged mean, or shared/untraceable reference ancestry.

**Important:** SHA-256 detects post-capture mutation; it cannot prove the first bytes were actually captured by a physical sensor or that their values are accurate. Every truth value and receipt issuer is simulated. There is **zero real physical qualification**.

Full exact locally tested `experiment.py` SHA-256: `8b6d9c34cfdea11743d56936ec581bedda4f1683b7de9bf40c34416df8fa923b`. The GitHub Python file is a separately authored runnable minimal reproduction. The local evidence ZIP contains exact executed code, 3,840 individual checks, seed-level results, hash-chained decision samples, and source manifest. GitHub checkout and live Pages execution are not independently verified.

[Python reproduction](experiment.py) · [Local results](results.csv) · [Manifest](manifest.json) · [Interactive lab](index.html) · [Phase IX tracker](../PHASE-IX-STATUS.md).
