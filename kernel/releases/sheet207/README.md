# SHEET 207 — Controlled Original WAL Owner Fencing

Verified locally: **13/13 PASS** using original S176 Node worker, Python WAL verifier, POSIX advisory lock, and three SQLite ownership epochs. Stale owner, resource mismatch, nonce replay, and epoch change before execution rejected.

Complete exact tested archive: `SHEET207-controlled-writer-fencing.zip`, 73109 bytes, SHA-256 `9517a27d1cba5ea4f98e1a76a0bb2699cce91b816cdbd2ab47e7c788845a05d2`. Includes `gate207.py` and all S206 predecessor code.

**Boundary:** Original S176 writer can still be invoked directly; owner issuance does not honor shared flock; check/append are not atomic. No mTLS challenge, independent physical host, hard power-loss, or historical full regression. Next S208 must enforce epoch inside writer and fence owner issuance.
