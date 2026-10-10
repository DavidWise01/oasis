# ROOT0 P4.34 — self-contained signed CAS crash regression (2026-10-10)

**Local Node v22.16.0 executed:** 28/28 assertions PASS. Final rerun elapsed **161.925 ms** (four child startups plus actual SIGKILL). Tested kill points: BEGIN IMMEDIATE -> recovered epoch 0; intent insertion -> epoch 0; witness head update before commit -> epoch 0; after COMMIT -> epoch 1. Each recovered head signature verified, exactly one signed fork wins and idempotent retries preserve the committed history.

**GitHub alignment:** `docs/reality-tensor/dyson-inversions/p434_cas.mjs`, `p434_worker.mjs`, `test_p434.mjs` have been committed and verified individually via GitHub fetch. This **self-contained regression has no P4.29/P4.30/P4.31 imports**; its signed intent codec is embedded in P4.34. Run `node test_p434.mjs` from a checkout with Node.js 22+. A clean checkout itself has **not** been executed in this environment, so clean-checkout reproducibility beyond inspection of committed files remains pending.

Exact local bundle SHA256: `5189fd750c79b2f1ddcb42f634b50872b4af6f8bfdec0227b00257e0fc6d8e79`.

**Limits:** SQLite local atomic transaction only, not independent storage or distributed atomicity. No hardware power loss, credential compromise, correlated rollback or external-host attestation. This is a reproducible local demonstration, not production witness certification.

Next P4.35: run a true fresh-clone GitHub CI matrix and isolate witness owner key and storage from controller trust domain.