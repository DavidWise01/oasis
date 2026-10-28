# Harvester v16.1 — Chromium execution gate (2026-10-21)

Status: **BLOCKED** (not passed). This checkpoint records observed execution, not a certification.

## Executed locally

- Command: `cd /mnt/data/harvester-v16-1 && node --test *.test.mjs`
- Result: **25 tests passed, 0 failed, 0 skipped** (Node v22.16.0).
- Chromium executable: `/usr/bin/chromium`.
- Playwright launch: **success** with headless Chromium.
- Playwright navigation to `data:text/html,ok`: **failed** `net::ERR_BLOCKED_BY_ADMINISTRATOR`.
- Without navigation, Chromium page is `about:blank`; attempting `indexedDB.open(...)` there failed with **SecurityError: access to the Indexed Database API is denied in this context**.

## Interpretation

The local Node tests cover journal transitions and read-only observer behavior, including receiver ledger simulations. They do **not** prove Chromium IndexedDB persistence, cross-tab contention, process interruption, or power-loss recovery. The previously committed `anny-chromium-gate.html` is still awaiting execution in an allowed Chromium origin, such as `http://localhost` or HTTPS.

## Reproduction / next acceptance gate

1. From this directory on a regular workstation, serve the files with `python -m http.server 8765`.
2. Open `http://localhost:8765/anny-chromium-gate.html` in Chromium and press **Run checks**.
3. Save the JSON result and browser version in an evidence file.
4. Separately, run real browser termination/restart and concurrent-tab tests with the same persistent profile.
5. Mark gate PASS only if those tests actually execute and all assertions succeed; retain failed logs otherwise.

Do not close Tasks 1, 2, or 3, merge draft PR #6, or modify frozen v12–v15 based on this checkpoint.
