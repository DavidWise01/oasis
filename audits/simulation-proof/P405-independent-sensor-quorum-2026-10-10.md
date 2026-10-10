# P4.05 Independent sensor quorum benchmark — 2026-10-10

Local Node 22.16.0 run: **16 assertions passed** in 238.585 ms. Three sensor identities each authenticate seven BigInt clock readings with separate HMAC keys. Gate uses at least two agreeing sensors within 0.08ms. No hidden true clock values inform the acceptance gate; the simulation uses ground truth only afterward to measure unsafe acceptance.

121 cycles x 200 layers per scenario:
| Scenario | Accepted | Quarantined | Simulated late | Oracle unsafe accepts |
|---|---:|---:|---:|---:|
| Normal | 24184 | 0 | 16 | 0 |
| One biased authorized sensor | 24184 | 0 | 16 | 0 |
| Two coordinated biased sensors | 24184 | 0 | 16 | **3996** |
| Missing two sensor reports for 20 cycles | 20188 | 4000 | 12 | 0 |

**Significant open security gap:** a majority of faulty or compromised but authorized sensors can agree on incorrect clock calibration. HMAC proves identity/integrity, not actual clock truth; multiple correlated sensors may similarly fail. Independent time origins and a durable non-rollbackable +1 witness are not implemented.

Preserved symbolic constraints: 200-layer/200ms clock, 1e-36-second BigInt register, exact blockade `{-{+{%}+}-}`, DIATOM 60-point z=0 conceptual harness. This run tests synthetic timing and authentication, NOT actual optical/physical time, quantum decoherence, or hardware synchronization.

Runnable standalone source, test, README and JSON results are included in conversation P4.05 ZIP; GitHub commit covers this audit only.