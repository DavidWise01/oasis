# AETHER-163 — Original Physical Capture Package and Timebase

**Phase XI Turn 3 of 8. Synthetic software protocol readiness 37.5%. Empirical physical qualification 0%. All operational ACT HOLD.**

The **locally executed** audit passed **3,200/3,200 deterministic checks** across 25 seeds × 8 scenarios × 20 ticks × two policies. Signed-only comparator: **1,200 unsafe dry-run ACT**. Capture/time gated: **zero unsafe dry-run ACT**, while preserving **2,800 safe dry-run ACT** (500 clean; 500 valid mock clock rotation).

Six fault regimes: missing original bytes, mutated original bytes, sample counter gap, clock rollback, forged absolute timebase anchor, and substituted capture-source identity. The gate verifies SHA-256 of preserved original bytes, source identity, signed clock label, nonce, generation, three monotonically counted samples separated by exactly 10 ms, and risk upper bound.

**Physical evidence is absent.** Absolute clock timestamps, original bytes, signing roots and acquisition data were generated in software. [Physical capture register](physical_capture_register.json) leaves all real instrument, clock and calibration fields null. An intact capture file cannot prove that an instrument generated it or that its clock is accurate. No physical sample or external calibration source was independently verified.

Exact locally executed `experiment.py` SHA-256: `f7f97695000d4cb20f1f1daee7aeabfcc28adb25dcad46bd43b6a61b2736f04c`. The complete local executed source, all 3,200 check rows, seed results, SHA-256 traces, manifest and register are in ZIP SHA-256 `170fe43fc7588c08890ab72a66492f30a3afbbdc831996576d10af869e004916`.

**Publication distinction:** GitHub `experiment.py` is a separately authored short reproduction; independently verified GitHub-checkout execution and live Pages deployment remain unavailable. This does not change the locally tested result.

[GitHub Python companion](experiment.py) · [Results](results.csv) · [Manifest](manifest.json) · [Physical register](physical_capture_register.json) · [Interactive lab](index.html) · [Phase XI tracker](../PHASE-XI-STATUS.md).

Next AETHER-164: traceable physical calibration and an evidence-derived uncertainty budget, keeping physical qualification at zero without genuine records.
