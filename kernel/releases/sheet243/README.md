# SHEET 243 — Triple-Service Crash Recovery

**Executed:** S243 39/39 PASS, S241 21/21 PASS, S235 15/15 PASS: **75/75 assertions across three focused suites**. The S243 gate runs original S176 Node WAL, separately running mTLS target/floor and UID-isolated Unix broker. Target, floor and broker die with overlapping SIGKILLs after signed receipts are persisted; a status request fails during the outage. All restart, exact receipts are recovered; forged statements denied; one authorized broker repair; replay denied. Post-commit broker restart retains floor/binding.

**Exact runnable release**: SHEET243-triple-service-crash-recovery.zip; 57 files, 81,772 bytes; SHA-256 `7cfd62fd1278f630155cadf2a91e89fd14653ecead3671333dc59bc2cf1be79c`. ZIP integrity passed. Contains `gate243.py`, `gate242.py` and all inherited original Node and Python modules.

**Progress:** 90% = 9/10 tracked local engineering milestones; *not* a production-readiness score.

**Limits:** one physical Linux host, generated testing certificates, no true network partition, hardware power loss, hostile concurrent WAL writes, or cross-store atomic guarantee. Next SHEET 244: transport partition/ACK uncertainty and deterministic recovery against persistent generation.