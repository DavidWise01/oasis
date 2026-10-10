# SHEET 201 — Target-Owned Proof Enforcement

Verified locally: **10/10 PASS** (`python gate201.py`). Original S176 Node dispatcher emits WAL; new target-owned verifier directly reads and audits original WAL and actual S179 SQLite row, then issues S198 signed receipt. Replayed exact request returns identical receipt; missing target, torn WAL, wrong scope/cursor, tampered target chain rejected.

Complete executable archive: `SHEET201-target-owned-proof.zip` SHA-256 `bff337eb5f53820d38f819cd748172a14a31d171b8f40beb177a2a0ed50ac4ab`, 51801 bytes. This source module requires S199/S198/S179 dependencies included in ZIP; gate test source also in ZIP.

Important: target-owned proof logic is not yet called inside the S197 mTLS HTTP handler; test harness supplies local filesystem paths. No separately hosted remote proof service, cross-store atomicity, power-loss test, or full historical regression.

Next S202: service-side fixed WAL and DB paths and integration into authenticated target HTTP lookup.
