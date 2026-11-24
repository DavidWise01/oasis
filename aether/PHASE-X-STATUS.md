# AETHER Phase X — Physical Reference Acquisition Setup and Evidence Intake

**AETHER-153 synthetic commissioning protocol PASSED. Phase X software setup readiness: 1/8 = 12.5%. Empirical physical qualification: 0% (NO PHYSICAL INSTRUMENT VERIFIED). Operational authority: HOLD.**

Phase X distinguishes *software protocol development* from *actual independent reference equipment acquisition, calibration and measurements*. Passing the former cannot advance the latter. This ledger does not claim that any instrument is physically attached or any traceability certificate has been authenticated.

| Turn | Bound | Acceptance | Software setup readiness |
|---|---|---|---:|
| 1 | 153 Equipment register and commissioning contract | **ACCEPTED — synthetic only** | **12.5%** |
| 2 | 154 Independent reference identity and certificate intake | Planned | 12.5% |
| 3 | 155 Original physical-capture file and timing intake | Planned | 12.5% |
| 4 | 156 Reference traceability and uncertainty budget | Planned | 12.5% |
| 5 | 157 Same-path hardware challenge procedure | Planned | 12.5% |
| 6 | 158 Physical drift/alarm acceptance thresholds | Planned | 12.5% |
| 7 | 159 Unknown-fault blind physical intake rehearsal | Planned | 12.5% |
| 8 | 160 Real-world qualification evidence decision freeze | Planned | 12.5% |

## AETHER-153 — Physical-reference acquisition setup boundary

- Exact local synthetic execution: 25 seeds × eight cases × 20 ticks = **200 paired episodes, 4,000 decisions per policy**, **3,200/3,200** deterministic acceptance checks.
- Baseline signed-only: **1,200 unsafe dry-run ACT**. The setup-gated controller: **zero unsafe dry-run ACT**, **2,800 safe dry-run ACT** retained, including **500/500 clean** and **500/500 reference rotation**.
- Six constructed faults were quarantined: missing reference serial, untrusted lab, expired calibration, missing raw capture, unverified route and challenge mismatch.
- An explicitly *uncommissioned* [equipment register](153/physical_setup_register.json) leaves serials, certificate provenance, calibration dates, actual measurement data, reference acquisition route and uncertainty blank. No hardware was connected or independently measured; **physical qualification remains 0%**. All operational ACT remain HOLD.
- Exact locally executed source SHA-256 `e61bcff26a003ae570a8279b57f45709e15fabb42cd1ad285a250db14e9a069b`; source plus 3,200 checks, seed results, traces and manifest preserved in locally generated ZIP.
- [GitHub AETHER-153 source, results, manifest, interactive HTML](153/) are committed. The GitHub Python is separately authored (not byte-identical to the local run); independent checkout replay and live Pages deployment remain unverified.

## Next AETHER-154

Define quarantined intake for actual reference instrument identity and calibration certificate credentials, retain nil values when unknown and forbid importing simulated fixture assertions as measured physical evidence.

One controller. Forward-only evidence. `{24/[2]/[4]/(3)/(3)/(1)/(1)} · {{i}} · .dlw`.
