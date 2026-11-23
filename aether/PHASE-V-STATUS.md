# AETHER Phase V — Live Progress

**AETHER-117 failed its no-unsafe gate. 4 / 8 turns = 50% (unchanged).**

| Turn | Bound | Status | Completion |
|---|---|---|---:|
| 1 | 113 Verified ingress | **ACCEPTED** | **12.5%** |
| 2 | 114 Key rotation and expiry | **ACCEPTED** | **25%** |
| 3 | 115 Schedule freshness and delayed retirement | **ACCEPTED** | **37.5%** |
| 4 | 116 Temporal freshness | **ACCEPTED** | **50%** |
| 5 | 117 Anchor continuity and reacquisition | **FAILED; revise as 117B** | **50%** |
| 6 | 118 Verification economy | Planned | 50% |
| 7 | 119 Unseen ingress stress | Planned | 50% |
| 8 | 120 Integration freeze | Planned | 50% |

## AETHER-117 — Failed acceptance, preserved

- 40 synthetic seeds × seven anchor/counter scenarios × 36 ticks × two paired controllers.
- **2,240/2,240** deterministic checks passed; **verified restart recovery 40/40** and clean availability 1,440/1,440 were preserved.
- Weak verifier **2,600 unsafe authorizations**; continuity-aware verifier **40 unsafe authorizations**. The all-unsafe-eliminated acceptance gate **FAILED**.
- All 40 failures arise in the delayed-anchor case: a currently valid anchor can coincide with falsely clean risk observations during an actual hazard.
- Chronology is necessary but not sufficient for permission to ACT. The controller must require fresh risk evidence independent of the timing certificate.
- [Failed executable and report](117/) preserved append-only. **No credit: Phase V remains at 50%.**
- **Next AETHER-117B:** bind reauthorization to post-anchor fresh-risk evidence on new seeds.

## AETHER-116 — Clock lease and drift evidence

- **60 held-out synthetic seeds × six clock-fault scenarios × 32 inspection ticks × two paired controllers**, 360 episodes per controller.
- **2,880/2,880** deterministic replay, chain integrity, unique decision and fail-closed checks passed.
- Wall-clock comparator: **1,200 unsafe authorizations**; monotonic signed-anchor verifier: **0**.
- Clean rotation safe actions preserved: **1,499** under each policy.
- Total modeled cost: wall-clock **766,774.4** versus monotonic **288,982.4**, a reduction of **477,792** illustrative cost units.
- **All five gate conditions passed.** The source code, numerical summary, manifest and interactive HTML are archived at [116](116/).
- **Assumptions:** authentic signed time anchor, unrollbackable monotonic counter, drift bounded by 0.1 tick/tick, uncompromised HMAC fixture keys. This is not a field safety guarantee.
- **Next AETHER-117:** time-anchor freshness and counter continuity.

## AETHER-115 acceptance evidence

- 80 synthetic seeds × six credential-feed conditions × 28 ticks × two paired policies.
- **1,600 unsafe authorizations** under indefinite schedule caching versus **zero** under four-tick schedule leases.
- Clean rotation retained **1,759 safe ACT** decisions in both policies.
- Total illustrative cost: **917,548.8 cached**, **338,732.8 leased**; savings **578,816**.
- Availability tradeoff: safe HOLD decisions increased from **164 to 484**, including delayed notice and outage recovery.
- All five declared gates passed: no added unsafe authorization, strictly fewer unsafe authorizations, clean-rotation preservation, lower total cost and exact replay. The synthetic trace archive is preserved at [115](115/).
- **Important limits:** packet signing keys are fixture secrets; authentic schedule authority and local tick clock are assumed. Active-key compromise, falsified time, and independently verifying correlation remain unsolved.
- GitHub source committed; live Pages deployment remains unverified.
- **Next AETHER-116:** clock rollback, drift and expiry ambiguity, under one controller.

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
- AETHER-115 completed with the separate bounded-lease test recorded above.

The governing decision authority remains one deterministic ACT/HOLD controller. If witness agreement or Byzantine problems become necessary, close and freeze this phase at its current real percentage.

[Phase V charter](PHASE-V-113-120.md) · [Frozen Phase IV](PHASE-IV-STATUS.md)

`{24/[2]/[4]/(3)/(3)/(1)/(1)} · {{i}} · .dlw`
