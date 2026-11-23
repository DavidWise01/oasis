# AETHER Phase V — Live Progress

**AETHER-114 accepted (synthetic). 2 / 8 turns = 25%.**

| Turn | Bound | Status | Completion |
|---|---|---|---:|
| 1 | 113 Verified ingress | **ACCEPTED** | **12.5%** |
| 2 | 114 Key rotation and expiry | **ACCEPTED** | **25%** |
| 3 | 115 Attestation limits | Planned | 25% |
| 4 | 116 Temporal freshness | Planned | 25% |
| 5 | 117 Homeostatic reacquisition | Planned | 25% |
| 6 | 118 Verification economy | Planned | 25% |
| 7 | 119 Unseen ingress stress | Planned | 25% |
| 8 | 120 Integration freeze | Planned | 25% |

## AETHER-113 evidence

- 50 seeds × 7 scenarios × 24 ticks × 2 policies.
- Trusted controller: **0 unsafe authorizations** versus **2,000** for the naive policy.
- Clean action preservation **800/800 (100%)**.
- Four deterministic properties passed on all 700 cases: **2,800/2,800 checks**.
- Strong assumptions: toy trusted authentication key and truthful independence certification by the acquisition layer. Source authenticity is not proof of source independence.
- Reproducible [source, summaries and HTML](113/) are archived.
- AETHER-114 credential expiry and key rotation tested separately; see evidence below.
- **GitHub Pages source committed; live deployment not yet verified.**

## AETHER-114 acceptance evidence

- 60 evaluation seeds × seven credential scenarios × 24 ticks × two paired controllers = 840 cases.
- **3,360/3,360** deterministic replay, chain-integrity, fail-closed and admissibility checks.
- Keyring-only comparator: **720 unsafe authorizations** across three old-key misuse conditions.
- Epoch-bound controller: **0 unsafe authorizations** in these test conditions.
- Clean rotation preserved **960/960** legitimate safe actions.
- Trusted rotation schedule and retirement notification are **assumptions**; a compromised active key is not detected.
- Reproducible [source, numerical audits and interactive lab](114/) committed.
- **Next: AETHER-115 — Rotation-Schedule Freshness and Revocation-Notice Delays.**

The governing decision authority remains one deterministic ACT/HOLD controller. If witness agreement or Byzantine problems become necessary, close and freeze this phase at its current real percentage.

[Phase V charter](PHASE-V-113-120.md) · [Frozen Phase IV](PHASE-IV-STATUS.md)

`{24/[2]/[4]/(3)/(3)/(1)/(1)} · {{i}} · .dlw`
