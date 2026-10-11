# ROOT0 P4.67 — checkout-relative runner and Actions workflow (2026-10-11)

**Local PASS 21/21** in fresh repository-shaped staging directory: P4.45 cross-UID signed witness **13/13**; P4.46 socket recovery **8/8**. Latest local runner measured 411.68ms and 29.319ms in component tests. Node.js v22.16.0, Linux root permissions and setpriv. Source dependencies from the previously built P4.47 bundle were copied into a clean staging tree; runner is relative to its own source path and checks exact assertion count, exit status, and timeout.

Committed `docs/reality-tensor/dyson-inversions/p467_repo_gate.mjs` and `.github/workflows/root0-p467-regression.yml`. GitHub statuses query returned no statuses; PR-filtered workflow run query returned zero. These do **not** verify hosted CI passed. The GitHub workflow depends on Node 22, root/sudo and setpriv and needs actual hosted validation. The old 42-assertion P4.66 runner remains a local bundle using paths not all synchronized to repository; P4.67 provides 21 portable tests, **not** 42. The earlier P4.45 integration tests were local Linux UID separation only. No independent-host admin domain tested.

Milestone ledger remains **15/20 = 75%**. CI certification cannot be counted before an actual successful workflow run. Deliverable ZIP SHA256 `19204111e25df0814b5da7c948533a22e96ed779b579acce00ea47de9635ba1b`.

Next P4.68: verify hosted GitHub Actions, synchronize remaining P4.64/P4.65 modules/test, and obtain independent external anchor custody evidence.