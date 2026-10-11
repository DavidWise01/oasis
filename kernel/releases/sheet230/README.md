# SHEET 230 — Verified Writer Bindings

Actual fresh runs: 16/16 `gate230.py` and 18/18 inherited `gate228.py`: **34/34 focused checks PASS**. Eight competing binds: 1 accepted, 7 stale rejects. Checks reject bogus WAL heads, nonce substitutions, incorrect sequence/owner, replays and recomputed-hash inconsistent commit pairs. `broker230.py` extends the S228 cryptographic broker: writer `bind` performs WAL validation under SQLite `BEGIN IMMEDIATE` before advancing bound head and append audit record.

**Runnable exact-tested ZIP**: `SHEET230-verified-writer-binding.zip` 138077 bytes, SHA256 `de7f860943c7cb7e5118c97563a667cad2e90e4c7a3234133f4c500d23a968eb`. Contents: `broker230.py`, `gate230.py`, S228 modules and gate, baseline S228 ZIP.

**Incomplete acceptance:** Broker-exclusive OS DAC for control DB and its `-wal`/`-shm` files **not implemented**. No live mTLS regression or physical crash test in S230. WAL itself is not held under an exclusive cross-store lock; noncooperative writers remain possible.

Next S231: broker-private UID and file ownership plus end-to-end dedicated-UID signed recovery.