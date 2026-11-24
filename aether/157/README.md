# AETHER-157 — Same-Path Hardware Challenge Procedure

**Phase X Turn 5/8. Software setup readiness 62.5% (synthetic only); physical qualification 0%.**

The exact local experiment ran 25 seeds × eight scenarios × 20 ticks, or 200 episodes/4,000 decisions per policy. **3,200/3,200 checks passed**, covering replay, SHA-256 evidence chain, tick order, one action, modeled safety, clean availability, operational HOLD and hidden-label isolation. Signed-only acceptance admitted **1,200 unsafe dry-run ACT**; the path-gated controller admitted **zero**, preserving **2,800 safe dry-run ACT** (500 clean, 500 legitimate rotation).

Six fault regimes: missing probe, pulse bypass, reference route swap, replayed pulse counter, late signal propagation and false physical coupling assertion. The synthetic gate binds DUT/reference/pulse source records by serial, challenge nonce, generation, acquisition route and counter; checks original raw byte hash, declared pulse amplitude, response time and capture time.

**Limit:** Pulse and reference records originate from one software fixture, so their agreement cannot demonstrate physical co-location or prevent a malicious common-root simulation. The [physical register](physical_path_register.json) is deliberately uncommissioned with null serials and trace fields. Real-world operational authority stays **HOLD**.

Exact executed local Python SHA-256: `924bd012dbaba31647692a96744985935abbe09f7ef858abae2c67f3b529e82e`. The GitHub Python demonstration is separately authored and has not undergone checkout execution. The local ZIP includes the exact tested code, 3,200 checks, seed results, trace samples, manifest and register. Live Pages deployment unverified.

[Python demonstration](experiment.py) · [Local results](results.csv) · [Acceptance manifest](manifest.json) · [Physical path register](physical_path_register.json) · [Interactive lab](index.html) · [Phase X tracker](../PHASE-X-STATUS.md).

**Next AETHER-158:** Drift and alarm acceptance thresholds using physical evidence only where actual source files exist, never synthetic evidence counted as metrology.
