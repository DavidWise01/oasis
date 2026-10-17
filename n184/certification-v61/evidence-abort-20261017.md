# N184 v6.1 — Aborted transaction evidence

**Date reported:** 2026-10-17
**Source:** user-supplied output from the N184 v5.9 two-tab certification console.
**Evidence type:** Operator-observed browser result; not independently reproduced by the assistant.

## Verbatim console output

```text
ABORT INJECTED_ABORT
UNCHANGED PASS
```

## Finding

**ABORT INTEGRITY — PASS (user-reported).** The test deliberately aborted a write and compared the stored state before and after. The test console reported that the checkpoint was unchanged.

This result adds to the previously recorded **two-tab CAS contention PASS** with `LOCAL PASS / REMOTE STALE / FINAL {"revision":1,"commits":1}`.

## Still pending

1. After an actual page refresh, use **Reload / inspect** and record the persisted revision and commit count.
2. Run **Run deterministic checks** to verify all 38,400 address/state mappings and frozen geometry calculations.
3. Real power-loss durability and external network reliability remain outside this browser integrity test.

No existing files overwritten. Frozen box/toroid geometry unchanged. No claim of physical quantum tunneling.
