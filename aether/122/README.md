# AETHER-122 — Selective calibration evasion

**Accepted on synthetic gate:** 7 scenarios × 60 held-out seeds = 420 paired episodes (10,080 ticks per controller). **5,040/5,040 checks** passed.

The original challenge-mode sensor can return correct public calibration responses while systematically understating risk in ordinary signed packets. The correction places hidden, committed known-value digital pilot inputs in the **same ordinary measurement path**, refusing ACT unless pilot outputs match. The test assumes these pilots are indistinguishable to the sensor until after it commits; this assumption is **not** established by HMAC or software alone.

| Controller | Unsafe ACT | Safe ACT | Illustrative cost |
|---|---:|---:|---:|
| Public challenge only | 1,544 | 4,860 | 919,520.0 |
| Opaque pilot gate | **0** | **2,580** | 279,148.8 |

Clean safe ACT **840/840** preserved; shifted-risk safe ACT **660/660** preserved. In faulty regimes extra HOLDs are intentional and expensive for availability. Positive bias is not detected by the particular saturating high-value pilot: it generates no unsafe ACT in the tested model but remains an important blind spot. Signed-but-selective outputs remain untrustworthy absent concealed same-path testability.

**Crucial limitations:** Secret probe placement/indistinguishability, trusted insertion, accurate known-value pilot ground truth, protected acquisition counter and HMAC key are assumptions. A sensor that can recognize probes, selectively target physical channels or forge probe results can defeat the method. No independent corroboration or witness/quorum algorithm; synthetic-only.

Run `python experiment.py` (NumPy and SciPy). Outputs: `results.csv`, `checks.csv`, `seed_results.csv`, `trace_samples.csv`, `manifest.json`. Original failed designs are not overwritten. Phase VI accepted turns 121–122, progress **25%**.
