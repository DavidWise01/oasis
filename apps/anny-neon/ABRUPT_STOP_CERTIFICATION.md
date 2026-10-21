# ANNY v16.1 — Abrupt Chromium Stop Boundary

**Scope:** `apps/anny-neon/`; synthetic 40-bit lab transfer only.  
**Main Pages:** `/apps/anny-neon/`  
**Isolated crash lab:** `/apps/anny-neon/crash-gate.html`  
**CI workflow:** `.github/workflows/anny-abrupt-stop.yml`

## What the new gate does

The external Playwright/CDP driver (`tests/abrupt_kill_gate.py`) starts a dedicated headless Chromium browser process group with a new on-disk browser profile. At each of five checkpoints, it waits for the corresponding IndexedDB transaction API to resolve and for independent observer reads to return. It then sends **SIGKILL** to only that dedicated process group and launches a new Chromium process using the SAME profile and localhost origin.

| Checkpoint before SIGKILL | Persisted journal expected | Receiver ledger effect | Read-only slot 18 |
| --- | --- | ---: | --- |
| PREPARED | PREPARED | 0 | HELD |
| COMMITTED | COMMITTED | 0 | HELD |
| RELEASE_PENDING | RELEASE_PENDING | 0 | HELD |
| RECEIVER_RECORDED | RELEASE_PENDING | 1 | HELD |
| CONFIRMED | CONFIRMED | 1 | VERIFIED |

After reopening, the test uses **new** `IndexedDBJournalStore` instances for the journal and receiver, re-reads both, checks transfer identity and digest, and confirms no automatic release occurred on page load.

An explicit synthetic `resume` call then follows a fail-closed rule:

- PREPARED/COMMITTED: remain **HELD**, with no receiver effect.
- RELEASE_PENDING with NO receiver receipt: call synthetic receiver delivery once, then verify its independent receipt before confirming journal.
- RELEASE_PENDING with receipt ALREADY recorded: re-read receipt and finish journal confirmation **without new delivery**.
- CONFIRMED: verify both persisted receipts and perform no operation.

After confirmation, five concurrent duplicate deliveries must preserve `effectCount=1`, and a forged independent receipt must yield `AGREEMENT FAILED`.

### Run on a clean checkout

```bash
python -m pip install 'playwright==1.57.0'
python -m playwright install chromium
node --test apps/anny-neon/crash-lab.test.mjs
python apps/anny-neon/tests/abrupt_kill_gate.py
```

Optional: `ANNY_CHROMIUM_EXECUTABLE=/usr/bin/chromium`, `ANNY_BROWSER_ARTIFACTS=/path/to/evidence`.

Artifacts include `abrupt-kill-summary.json`, per-stage JSON reports, and post-reopen screenshots. A CI run passing all five stages is the **first defensible browser-level forced-process-termination checkpoint**. No browser-level passage should be claimed until an actual execution report is reviewed.

## What this does not prove

The SIGKILL occurs **after** the selected IndexedDB transaction promise has resolved. It does NOT simulate termination inside an uncommitted transaction, sudden electrical power removal, filesystems losing unflushed data, cross-machine federation, or externally observable exactly-once effects. Chrome's strict IndexedDB transaction durability request is used by the preexisting adapter, but not a substitute for a power-cut rig.

The new lab uses `anny-abrupt-boundary-v16-1-*` IndexedDB namespaces and does NOT alter the regular ANNY live lab, 10 ACK observations, 18-slot analytical cubit, radiation displays, Sapphon signed bands, `-- VOID`, or `++ GRAVITY`.

## Static model evidence at commit time

The pure classifier in `crash-lab.test.mjs` was executed separately in V8 and passed **9/9** on committed source. This is NOT a browser process-restart result. Full Chromium SIGKILL results must come from a GitHub Actions run or local invocation of the Python driver. The repository workflow and browser lab have been committed; remote runner success must be verified independently.
