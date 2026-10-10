# SHEET 197 — Dual-Process Authority Recovery

**Executed locally:** `python gate197.py` — **18/18 PASS**. Target receipt and floor authority each run as a separate subprocess with separate SQLite state and separate Ed25519 signing keys, using mTLS. Target SIGKILL and restart retains its signed receipt; floor SIGKILL and restart retains exact signed floor ACK; mismatched receipt, unauthorized client, stale floor generation and target outage fail closed.

Complete runnable ZIP: `SHEET197-dual-process-authority.zip` (11,216 bytes), SHA-256 `3c2b83013ca886b10534dbbc87198ae1b101f762e4ca91f8ea5034649e2d386d`. Includes `gate197.py`, `server197.py`, `target196.py`, `authority193.py`, `authority194.py`, `authority195.py` and README.

**Limits:** same physical host, common ephemeral test CA, synthetic target-commit requests rather than signed receipts derived from real S179 database writes, no original S176 WAL/repair integration, no physical power-loss or cross-host partition testing, and no inherited tests rerun. The GitHub `server197.py` depends on predecessor files supplied in the ZIP; the ZIP is the self-contained verified runner.

Next S198: enforce target-side resource and issuer scoping; integrate committed target evidence with the original S179 writer and S176 WAL before any distributed exactly-once claim.
