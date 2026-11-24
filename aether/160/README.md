# AETHER-160 — Phase X Qualification Evidence Decision Freeze

**Phase X synthetic software-protocol readiness CLOSED: 8/8 = 100%. Empirical physical qualification OPEN at 0%. All operational decisions HOLD.**

## Executed local acceptance

The complete local program `aether160/experiment.py` (SHA-256 `d053b735efac8ddb19f3efcd7f06e8e22d0fd4b42bf6032151e3bcac8fd279ac`) checked the SHA-256 of frozen `frozen_159.py` (`c02f6aa6bf43b46b0b0e92fa5b604c05392c6a237b7d0cde3c971a9a13cb4f56`) and imported its original, unmodified authorization code. It ran **25 fresh seeds × eight scenarios × 20 ticks × two policies = 200 episodes/4,000 decisions per policy**.

**3,200/3,200 deterministic checks passed**. Signed-only comparator allowed **1,200 unsafe synthetic dry-run ACT**. The frozen blind gate allowed **zero unsafe synthetic ACT**, preserving **2,800 safe dry-run ACT**, including 500 clean and 500 legitimate rotation. Operational ACT = **0**.

## Predecessor inventory

Seven Phase X predecessor ZIP archives (AETHER-153–159) were checked for ZIP CRC, executed source, accepted manifest, results and 3,200 passing checks each. `archive_inventory.csv` records archive and executed-source SHA-256 values. Earlier experiments were inventoried, **not rerun**. The original **failed** AETHER-154A manifest remains immutable, alongside the accepted correction.

## Physical qualification decision

**OPEN / 0%**. No actual reference standard, independent physical instrument, traceable calibration certificate, original physical raw capture, same-path hardware waveform, measured drift or measured alarm latency has been provided. The final [physical qualification register](physical_qualification_decision.json) records those as null. No real-world ACT is permitted.

**Reproduction boundary:** The exact locally executed source and frozen controller are in the [downloadable evidence ZIP](https://github.com/DavidWise01/oasis/tree/main/aether/160) *only as a separately distributed conversation attachment*, not the GitHub tree. GitHub's `experiment.py` is a separately authored checkout demonstration referencing GitHub's separately authored 159 model, so its output must not be represented as byte-identical local execution. Independent GitHub checkout replay and latest Pages deployment are unverified.

[Interactive lab](index.html) · [Results](results.csv) · [Archive inventory](archive_inventory.csv) · [Acceptance manifest](manifest.json) · [Physical decision](physical_qualification_decision.json) · [Phase X tracker](../PHASE-X-STATUS.md).

**Next natural phase:** design a real-world acquisition and calibration evidence intake, but do not award physical qualification until actual independent measurements are authenticated. `{{i}} · .dlw`
