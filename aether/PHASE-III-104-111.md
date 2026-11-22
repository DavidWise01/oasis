# AETHER Phase III — Evidence Lineage and Adversarial Provenance

**Eight planned bounds: AETHER-104–111.** This is a new phase; AETHER Phase II was frozen and closed at AETHER-103 (100%). Independent ancestry and Byzantine-style evidence attacks are *explicitly in scope here*, not retroactively in Phase II.

## Governing principle

**One hegemonic controller. Diodic evidence flow.** Sources provide observations; they never acquire authority to choose the action. A certificate identifies the ancestry of each supporting observation. Duplicated reports from the same root do not multiply corroboration. The controller deterministically selects the only admissible action, or HOLD if evidence is insufficient.

| Turn | Bound | Acceptance question | Cumulative planned completion |
|---|---|---|---:|
| 1 | **104 — Root-Lineage Deduplication** | Can cloned evidence be counted once without suppressing genuine independent evidence? | 12.5% |
| 2 | **105 — Forged and Shared Ancestry** | Can spoofed root labels or hidden common upstream origins be detected or safely refused? | 25% |
| 3 | **106 — Conflict and Equivocation** | Can contradictory signed assertions from a source be quarantined and preserved? | 37.5% |
| 4 | **107 — Quorum Under Faults** | Which independent agreement rules preserve safety and liveness at declared fault budgets? | 50% |
| 5 | **108 — Asynchronous and Delayed Evidence** | Can stale and reordered reports be prevented from changing closed decisions? | 62.5% |
| 6 | **109 — Coordinated Adversarial Sources** | Can multiple dishonest or correlated roots be identified without treating identity as proof? | 75% |
| 7 | **110 — Byzantine Stress and Recovery** | What measurable limits remain under controlled faults and changing trust? | 87.5% |
| 8 | **111 — Integration and Freeze** | Does the entire evidence lineage and action gate reproduce, with preserved failures and audit? | 100% |

## Percent and closure rule

**Completed bounds / 8 × 100**. A bound counts only after reproducible tests meet its declared acceptance gate and source is verified in GitHub. A failed bound is archived and remains incomplete. GitHub Pages deployment is a separate verification state.

Stop and freeze at AETHER-111 after successful integration, or close early if a new independent primitive beyond the scope of source lineage/Byzantine evidence is necessary. Report actual percentage, not assumed 100%.

## AETHER-104 initial boundary

Synthetic report roots are supplied by trusted metadata. The first test measures duplicates and deliberately does not claim to defend against forged root identities; that is AETHER-105. Root agreement is evidence qualification, **not distributed governing authority**.

`{24/[2]/[4]/(3)/(3)/(1)/(1)} · {{i}} · .dlw`
