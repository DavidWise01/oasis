# SHEET 232 — Broker Live UID/Socket Authorization

Actual Linux-root test: **17/17 new checks PASS** running S232 broker as `daemon` UID, clients root/operator, bin/writer and nobody/repair. SO_PEERCRED authenticates socket peers. Private SQLite parent mode 0700, DB mode 0600 prevents writer/repair direct database access. Verified WAL binding, Ed25519 dual-signature repair, wrong-role denial, replay denial and broker restart persistence passed. Regression reruns S230 16/16, S228 18/18, S231 17/17: **68/68 focused checks** total.

Exact executable ZIP: `SHEET232-live-isolated-broker.zip` (14116 bytes, 10 members), SHA256 `486ea33e96a353774c65a3cae40b13ffb21ca6be36698baabe6b69348b19133e`. Full exact test `gate232.py`, S227/S228/S230 broker and S231 isolation source inside ZIP.

**Limitations:** Local, fixture-signatures and manually constructed WAL; not full live target/floor mTLS. Test socket parent is world-writable; socket mode 0666 relies on peer credentials for authorization and lacks rate limits. No cross-store atomicity, hostile WAL concurrent writer, hardware power-loss or root compromise protection. Next S233 must harden socket directory and wire actual mTLS target/floor evidence.
