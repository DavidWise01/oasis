# AETHER-165 — Same-Path Physical Challenge Evidence Package

**Phase XI Turn 5/8 · 62.5% synthetic software readiness · physical qualification 0% · operational HOLD.**

The exact local `experiment.py` passed **3,200/3,200** deterministic checks with 25 seeds × eight scenarios × 20 ticks × two policies (200 episodes / 4,000 decisions per policy). The signed-only comparator allowed **1,200 unsafe synthetic dry-run ACT**. The same-path gate allowed **zero unsafe** while preserving **2,800 safe dry-run ACT**, including 500/500 clean and 500/500 legitimate generation rotation.

Six simulated failures were missing probe, bypassed acquisition route, replayed challenge counter, delayed pulse propagation, substituted injection port and false probe response. Gate requirements include original capture SHA-256, signed DUT/probe/reference identity and nonce, current challenge counter, amplitude response, same input route and injection port, and a 50 ms propagation bound. These are simulation policy thresholds, not measured hardware performance.

**Physical evidence absent:** original sensor bytes, actual probe waveform, calibration certificate and physical injection path remain null in the [physical register](physical_path_register.json). Mock probe and reference belong to the same software test ancestry, so they cannot authenticate a physical shared path. Physical qualification stays **0%** and operational ACT stays **HOLD**.

Full *locally executed* Python SHA-256 `26f539f9e238d6dfcfd28e6b0f212571e25bf1e3ded71b77d7a4afc2b2e873fb`; full local ZIP SHA-256 `642d784c78e0c87ba83c864f4864859e0e57bfe333443a0d191f38b9bf14cbb1`. The ZIP includes all 3,200 check rows, seed results, source and SHA-256-chained decision traces.

**Reproduction limitation:** GitHub `experiment.py` is a separately authored compact program, not byte-identical with the full executed source. GitHub checkout replay and live Pages deployment have not yet been verified.

[Python companion](experiment.py) · [Results](results.csv) · [Manifest](manifest.json) · [Physical register](physical_path_register.json) · [Interactive lab](index.html) · [Phase XI tracker](../PHASE-XI-STATUS.md).

**Next bound:** AETHER-166 physical drift and alarm evidence intake, requiring actual samples for any change to physical qualification.
