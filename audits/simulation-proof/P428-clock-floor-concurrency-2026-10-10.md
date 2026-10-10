# ROOT0 P4.28 — clock regression and concurrent quotas (2026-10-10)

**Executed locally** using Node.js 22.16.0 experimental SQLite: **17/17 assertions PASS**, final rerun **142.838 ms**. Twelve separate Node processes issued 30 requests each to one shared SQLite DB: **360 total, 32 accepted, 328 rejected, 0 worker errors**. Retained cap 32. Time-regression challenge issuance and cleanup rejected, both before and after restart, using a persisted SQLite clock high-watermark in a `BEGIN IMMEDIATE` transaction. The watermark also survived process contention.

This is a local relative clock floor, not trusted physical time. Host-admin coordinated SQLite rollback removes its protection. P4.26 receipt verification still relies on Date.now, so this test does NOT solve verified receipt clock regression. Outstanding challenge accounting is global per DB while rate quota is per deployment; cross-deployment partitions require work. No independent host or certifiable remote authority.

Exact locally tested source, worker, test and output are in the conversation P4.28 ZIP: SHA256 `43f37b03af43f8191fd806c73cf1958664ed277dee95214b16901a50ce1a85a2`. This commit is the audit only; executable source has not been pushed.

Next P4.29: integrate clock floor into verification, isolate deployment quotas and test simultaneous deployments.