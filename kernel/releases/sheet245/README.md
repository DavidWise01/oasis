# SHEET 245 — Real TCP ACK Connection Reset

**Fresh checks:** gate245.py **32/32 PASS**; gate243.py **39/39 PASS**; gate235.py **15/15 PASS**; 86/86 across three runs. A live TLS-transparent TCP relay forwards the floor authorization request and closes its connection after confirming that the floor's SQLite signed_ack row exists. The client gets a real TCP reset with no response. Reconnecting directly over authenticated mTLS to `/status` returns the original signed Ed25519 receipt. An idempotent retry returns the identical receipt, and the broker commits one bound history/floor generation, rejecting replay.

ZIP: `SHEET245-tcp-ack-reset-recovery.zip`, 62 files, 89,538 bytes, SHA-256 `29bbcf68a42543a93369cb64a606474ce91a42733f27b497c8c917137c7212f5`; contains exact tested gate245.py, proxy245.py and inherited gates/source.

**Scope:** Same-host loopback TCP cut triggered by local DB observation, not independent remote network partition or packet loss. No physical power-loss, multi-host partition, cross-store atomic transaction, or production PKI evidence. **Progress 90% (9/10 locally demonstrated milestones)**; not production readiness.

Next S246: independent network namespaces with partition-and-heal, concurrent retries, preserved signed floor generation.
