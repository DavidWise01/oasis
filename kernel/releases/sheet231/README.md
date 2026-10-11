# SHEET 231 — Broker-Exclusive SQLite File Isolation

Executed `python gate231.py`: **17/17 PASS** on Linux with broker UID `daemon` (1) and unauthorized UID `nobody` (65534). Access denial verified for database read, write, truncate, unlink, chmod, and WAL/SHM sidecar creation. Private database directory 0700, SQLite file 0600. Previous `gate230.py` 16/16 and `gate228.py` 18/18 also passed, **51/51 across focused gates**.

Tested ZIP `SHEET231-broker-private-sqlite.zip`: 140,575 bytes, 10 entries; SHA-256 `809aa7dd24beec96b6331e40cbb04301f5aef981d7e5b07aec41089504498891`. It includes executable gate231.py, isolation231.py, broker230/228/227 modules, prior gates and S228 baseline ZIP. ZIP integrity passed.

**Remaining limits:** root and same-broker-UID processes remain trusted; broker UNIX socket was not deployed under separate broker UID in this gate; signed end-to-end mTLS crash recovery and cross-store atomicity were not retested. Next S232: deploy broker-private UID service with peer credential authorization, then validate signed floor repair and original writer binding over real sockets.
