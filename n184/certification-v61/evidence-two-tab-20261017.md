# N184 v6.1 — Two-tab contention evidence

**Observed / supplied by user:** 2026-10-17  
**Source:** user-reported output from [v5.9 certification console](../two-tab-certification-v59/)  
**Verification class:** first-party operator report; not independently replayed by assistant.

## Verbatim output

```text
Peer ready; both tabs read revision 0
LOCAL PASS / REMOTE STALE
FINAL {"revision":1,"commits":1}
RACE PASS
```

## Result / interpretation

- Both browser tabs began from checkpoint revision `0`.
- Local writer successfully committed.
- Remote writer received a stale-revision result.
- Final stored record was `{"revision":1,"commits":1}`.
- **Two-tab CAS contention gate: PASS (user-reported browser run).**

## Remaining gates

- Inject an aborted write and verify the record is unchanged.
- Reload and inspect the checkpoint; verify `revision:1, commits:1` remains (before any subsequent tests alter the test database).
- Run all 38,400 address/state reversible mapping tests in the browser.
- Actual browser crash, power-loss durability, and cross-device reliability remain outside this result.

The frozen N184 box / toroid / X-core model is unchanged. This tests software synchronization, not physical tunneling.
