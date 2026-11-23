# AETHER-135B — Independently rooted physical reference required or HOLD
**PASS in the restricted synthetic test**, 400 episodes × 32 ticks, **3,200/3,200** deterministic checks, **0 unsafe ACT**. Frozen AETHER-134 failed (fixed 800 unsafe / adaptive 1,250 unsafe ACT) in [AETHER-135](../135/).

A completely separate, trusted synthetic reference standard must supply a correctly authenticated current risk measurement, matching reference device, physical root, acquisition tick, instrument generation, and uncertainty bound. Forged root or missing reference evidence forces HOLD.

The guarded policy preserved **1,600/1,600** clean and **1,600/1,600** legitimate replacement safe ACT. Overall it authorized **4,400 safe ACT**, with **6,000 additional safe HOLDs** from lack of trusted reference during other scenarios. It bought **6,400 reference inspections**.

**No physical independence was measured**: a synthetic reference's correctness, signing root and separate measurement path are assumed. The additional gate does NOT magically detect undetectable physical deception; it simply refuses authorization without a designated trusted physical input. This is one deterministic controller, not witness voting/quorum/Byzantine logic.

The source published to GitHub is a separately authored repository-compatible implementation; source byte identity and checkout replay against local output are not verified.
