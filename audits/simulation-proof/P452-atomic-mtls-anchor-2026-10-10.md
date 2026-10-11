# ROOT0 P4.52 — Atomic TLS anchor + certificate binding (2026-10-10)

Local Node 22 regression **16/16 assertions PASS**, latest rerun **411.535 ms** including test OpenSSL certificate generation, service startup, TLS exchanges, actual SIGKILL and restart.

P4.52 moves the anchor and consumed request nonces into **one SQLite WAL database** using `BEGIN IMMEDIATE` and `synchronous=FULL`. TLSv1.3 transport requires a verified client certificate and enforces the exact configured SHA-256 leaf-certificate fingerprint, alongside Ed25519 signed requests and anchor responses. Local test covers authenticated checkpoint observation, rollback and conflicting history detection, nonce duplicate refusal, an unauthorized Ed25519 key, omitted TLS client cert, invalid CA, SIGKILL outage and durable restart.

**Limits:** Service explicitly listens only on 127.0.0.1 on one host, not an independent host. Certificate provisioning and storage are controlled locally, nonce table grows unbounded, no trusted remote rollback anchor, no client certificate rotation, no physically independent failure-domain test, no power-cut proof. Do not claim production readiness.

**Completion reporting convention requested by user:** label prototype roadmap as **13/20 milestones complete = 65%**; this is a planning metric rather than measured security maturity or global kernel completion. Report on every subsequent gate, update numerator only upon passing the next defined milestone. Production-grade independent-host readiness remains unverified.

Full executable server/client/test source and results in downloadable `p452_bundle.zip`, SHA256 `bc98da551c461300e42624dc535bea0ff4640f0e5b6a134488966cf535cf12a4`. This commit records audit only, not runnable P4.52 source.

P4.53 target: bounded durable nonce epoch rollover, certificate rotation, and a truly distinct-host test with separately controlled anchor storage.