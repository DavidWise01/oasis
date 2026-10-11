# SHEET 238 — Original S176 WAL with independently restarting authority services

**Executed on local Linux:** S238 integrated gate 36/36 PASS; S235 commit-boundary regression 15/15 PASS; S236 failure-fixture regression 16/16 PASS. **67/67 assertions across three suites.**

The new integrated gate runs the original S176 Node.js worker/transaction runtime for TWO real WAL prepare+commit transactions instead of hand-constructing WAL fixture records. It checks genuine hash-linked records and append-only committed prefix. Actual target and floor processes issue mTLS-signed receipts, get SIGKILLed and restarted separately; the original target receipt and persisted floor ACK survive. The daemon-owned broker uses those signatures to advance one binding/floor generation and persists through its own process SIGKILL; replay rejected. Missing client certificates, incorrect socket role and forged signatures rejected.

**Exact executable archive**: `SHEET238-original-wal-independent-recovery.zip` (69,084 bytes, 47 files), SHA256 `3407024c98bf7e02469eac39b487aec11d42c28ba68233bbd42035c9f8010709`. Contains `gate238.py`, `gate234_238.py`, `build238.py`, original `s176/*.js`, S235/S236 regression gates, and complete Python runtime dependencies. Run `python gate238.py && python gate235.py && python gate236.py` on Linux as root with Node.js, setpriv and cryptography installed.

**Security scope**: This is a test-controlled original S176 worker, not the fully isolated signed-ledger S220 writer service. Crashes are sequential across authority services, not simultaneous. Single physical host and generated PKI. No full cross-store atomic transaction, remote network partition or hardware power-loss proof.

**Progress:** 90%, 9/10 local engineering milestones. Not production-readiness. Final milestone requires coordinated mid-WAL failure plus target/floor lost ACK and uncertain broker commit in one failure-recovery lifecycle.

Next SHEET 239: crash original S176 writer mid-prepare, quarantine and reconcile without fabricating commit, while authorities and broker fail independently.
