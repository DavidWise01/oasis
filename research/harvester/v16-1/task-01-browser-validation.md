# Harvester v16.1 — Task 1 browser validation checkpoint

Date: 2026-10-21

## Local results
- `node --test journal.test.mjs`: **5 passed, 0 failed**.
- Browser test harness prepared for real IndexedDB transaction tests, independent store instances, concurrent idempotent commits, recovery and confirmation.
- Chromium executable located at `/usr/bin/chromium`.
- Browser execution **BLOCKED**, not passed: Playwright navigation to local test server returned `net::ERR_BLOCKED_BY_ADMINISTRATOR`. No indexedDB test result is asserted.

## Required next verification
Run `browser-test.html` from an allowed localhost or HTTPS origin with `journal.mjs` and `browser-check.mjs` alongside it. Verify concurrent commits, recovery after process restart, and durable confirmation in Chromium desktop/mobile. Extend to cross-tab writers and forced browser termination. The memory tests do not establish power-loss durability or exactly-once external effects.

## Scope discipline
Do not modify frozen v12–v15 artifacts. Task 1 remains open. v16.1 certification is withheld pending browser verification.
