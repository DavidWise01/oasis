# Boundary 06 — Conflicting duplicate packet identity

Source: `research/ket/boundaries/ket-boundary-06.html`
SHA-256 of committed local source: `26c11360b0147f3738ee8c7e49b1a6d7e5f9113b381d9c8cf65ffd04a63a73a0`

## Behavior
Compared with Boundary 04, the IndexedDB `atomicAppend()` now hashes the *request* (id, from, to, token, expected, actual) as `requestDigest`, stores it inside the receipt, and checks duplicate packet IDs against that original-input digest:
- exact same packet ID and input: `REPLAY` — no new receipt;
- same packet ID, differing input: `ID_CONFLICT` — no new receipt;
- new ID: normal transactional compare-head/write path.
- Hash chain includes the requestDigest, binding it to journal integrity.

## Test status
- **PASS:** JavaScript syntax check (`node --check`) on extracted module.
- **PASS:** Static source review of both the pre-read and in-transaction duplicate branches.
- **BLOCKED / NOT RUN:** Real two-tab browser race, reload and IndexedDB durability tests. Chromium Playwright navigation to local HTTP was blocked by `net::ERR_BLOCKED_BY_ADMINISTRATOR`.
- **NOT CLAIMED:** Benchmark timing, browser regression, concurrent-writer correctness, production exactly-once delivery.
- Boundary 04 was also not browser-tested. The legacy in-memory `transact()` helper still uses the old replay policy and must not be used as a substitute for this tested write path.

## Structural risk
The pre-read and write transaction head compare requires browser execution to establish actual contention semantics. Signing keys remain local; no independent signer or external receipt protocol has been built. A request digest distinguishes bytes of the logical packet but not adversarial origin.

## Next required evidence
Run a browser-accessible deployment on an HTTPS or localhost origin in a real browser, open two tabs and issue simultaneous writes with the same ID but different payloads. Confirm one COMMITTED, one ID_CONFLICT, exactly one row, full journal validation after both tabs reload. Perform forced tab close mid-write and recover. Export checkpoint and test with Boundary 05's independently pinned verifier.

`[[ BOUNDARY06 :: CONFLICTING-ID-REJECT :: SOURCE COMMITTED :: BROWSER EVIDENCE OPEN ]]`
