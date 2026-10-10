# SHEET 178 — Hard-Kill Fencing & Durable Cursor Reconciliation

**Actual local test results:** S178 22/22 PASS. Reran S177 20/20, S176 20/20, S175 26/26, S174 20/20, S173 22/22; 130/130 focused checks total.

The executable ZIP adds `fence178.js` (monotonic owner epochs, sequential target cursor, duplicate checks, uncertain WAL quarantine), `kill178.js` (actual child SIGKILL with filesystem lock held), and `gate178.js` (22-check gate). SHA-256 ZIP: `2b83411c13d204cb93ebf9284ea17ee3695cc37599063f0d73758c3f00d0b6c3`. Download available in the originating conversation as `SHEET178-hardkill-fencing-gate.zip`.

**Boundaries:** Simulated authority is a separate directory on one host, not a physically independent authority. Read/check/rename is not an atomic compare-and-swap across writers. No automatically safe stale-lock reclamation, no real target database atomicity, and no cross-host or live source/target Merkle integration. SIGKILL demonstrates abandoned lock persistence; it does not establish safe automatic recovery from it.

Next SHEET 179: target-side atomic fencing token enforcement, independently hosted authority, uncertain-commit resolution, power-loss fault injection.
