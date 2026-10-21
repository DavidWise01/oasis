# ANNY v16.1 — Midflight IndexedDB Atomicity Boundary

**Date:** 2026-10-21.  
**GitHub Pages:** `apps/anny-neon/midflight-gate.html`  
**CI:** `.github/workflows/anny-midflight-atomicity.yml`  
**Driver:** `apps/anny-neon/tests/midflight_gate.py`

## Next boundary: interruption BEFORE a transaction completes

Previous SIGKILL test checkpoints stopped **after** an IndexedDB transaction API had completed. This new gate sends SIGKILL while Chromium has an active `readwrite` transaction with chained pending `put` requests.

Two isolated scenarios use a new synthetic 40-bit transfer and distinct scratch IndexedDB namespaces (`anny-midflight-v16-1-*`):

| Interrupt during | Durable starting state | Tentative in-flight write | Expected after SIGKILL |
| --- | --- | --- | --- |
| `RECEIVER_WRITE` | Journal RELEASE_PENDING, receiver effect 0 | Receiver receipt + effectCount 1 + audit marker in same transaction | Journal RELEASE_PENDING, receiver effect 0, Violet HELD |
| `JOURNAL_CONFIRM` | Journal RELEASE_PENDING, receiver receipt + effect 1 | Journal CONFIRMED + matching receipt + audit marker in same transaction | Journal RELEASE_PENDING, receiver effect 1, Violet HELD |

The driver waits until the transaction is **RUNNING with at least five successful chained requests**, while `completed=false` and `aborted=false`, then kills the *dedicated* Chromium process group. The transaction cannot naturally complete before the 45-second safety timeout because requests chain until stopped.

**The expected result is rollback of all uncommitted writes.** The harness checks that the ledger and journal still represent the independently verified baseline. It uses a token held by the outside-browser Python driver rather than depending on `localStorage`.

After a successful rollback check, **explicit** synthetic continuation proceeds by independently reconciling the receiver before any delivery. The completed state must have effectCount 1 with matching journal/receiver receipts; five duplicate deliveries must preserve that count. A forged independent receipt must not mark Violet VERIFIED.

### Run

```bash
node --test apps/anny-neon/midflight-lab.test.mjs
python -m pip install 'playwright==1.57.0'
python -m playwright install chromium
python apps/anny-neon/tests/midflight_gate.py
```

The workflow saves a summary JSON, one report and screenshot per scenario to the `anny-midflight-idb-evidence` Actions artifact. A passing Actions result with both scenarios is required to claim Chromium midflight rollback.

## Isolation and limitations

- The test uses the real `CommitJournal`, `ReceiverLedger`, and `readAnny` APIs for setup, verification and explicit recovery. The **in-flight mutation itself** is deliberately placed directly into one outstanding IndexedDB transaction to control the kill point.
- This validates IndexedDB **transaction atomicity** under browser process termination. It is not a proof of arbitrary crashes throughout the Harvester's real two-transaction receiver/journal protocol or external side effects.
- It does **not** simulate electrical power removal, storage controller cache loss, kernel failure, disk corruption, or distributed exactly-once effects.
- `midflight-gate.html` never kills Chromium itself. It can auto-abort a manually armed transaction after 45 seconds.
- The normal GitHub Pages Harvester store, 18-position analytical cubit, 10 dual-path ACKs, seven Greek Sapphon pairs, White broadband, VOID/GRAVITY, and radiation overlay remain untouched.
- The isolated V8 harness executed **38/38 synchronous pure registry/model tests** against current committed source, zero failures. That is **not** a live Chromium pass.
- The previously observed `ERR_BLOCKED_BY_ADMINISTRATOR` for local browser navigation remains a reason not to claim local browser certification. Review GitHub Actions evidence after a run.
