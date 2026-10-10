# SHEET 215 — Target-Owned Commit and Durable Floor ACK

**Executed focused integration gate: 26/26 PASS** (`python gate215.py`). Actual S210/S208 Node WAL and real SIGKILL produce quarantine. mTLS target `/commit` persists a WAL-head-checked target record. Its `/attest` returns an Ed25519 statement. Separate mTLS floor `/attest` persists signed generation ACK in SQLite, with idempotent retry and `/status` recovering identical ACK after floor service restart. Conflicting history denied; forged and missing evidence preserve quarantine; valid S213 signed reconciliation resumes append.

**Full exact tested release:** [SHEET215-target-commit-durable-floor-ack.zip](https://github.com/DavidWise01/oasis/tree/main/kernel/releases/sheet215) distributed through ChatGPT conversation, 63,370 bytes, 46 files; SHA-256 `eccff84bd614571d2cb98d7e80ecf85e5536e4d332cc6c5f0ce4f1198b24cfb8`. Executable source `authority215.py`, `gate215.py` plus predecessors are packaged in ZIP, not this GitHub commit.

**Limitations:** The new target service commits a WAL-head-checked record, not via the full independent S179 production target executor. Its request metadata is caller-provided. Separate TLS server threads share one host and test-generated keys. No cross-store atomicity, distributed consensus, full historical regression, production UID re-test, power-loss, or remote host exercise.

Next SHEET 216: tie committed target record to actual target transaction executor, verify WAL prepare/commit semantic linkage and ownership, and test torn transactions and replay across separate processes.
