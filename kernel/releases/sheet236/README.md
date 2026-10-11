# SHEET 236 — Four-Store Fault Matrix

**Verified today:** `python gate236.py` **16/16 PASS**, inherited `gate235.py` **15/15 PASS**, inherited `gate234.py` **23/23 PASS**. Total **54/54 assertions across three separate runs**.

The new test launches real subprocesses and terminates them immediately after: (1) an incomplete WAL write, (2) a target SQLite INSERT before COMMIT, (3) a floor ACK INSERT before COMMIT, and (4) a broker SQLite binding INSERT before COMMIT. Recovery checks WAL partial-tail detection, SQLite rollback, durable floor ACK lookup after reopen, Ed25519 dual-signature broker reconciliation and replay denial. Original validated WAL prefix stays unchanged following repair.

**Exact runnable package:** `SHEET236-four-store-fault-matrix.zip`, 26,896 bytes, 17 files, SHA256 `d6405c4ca1dc091939dee6e17a0e0982e2cb4efac547236c58c833a184c645cc`; includes `gate236.py`, `gate235.py`, `gate234.py`, authorities, brokers and documentation.

**Security scope:** The new four-store test uses simplified failure fixtures, *not* fully independent four running production services. Live mTLS suite was rerun separately. Network partition, concurrent full-service SIGKILL, OS-restricted production deployment and physical power-loss consistency remain unproved. The ten-milestone checklist therefore stays at **90% (9/10)**, not production readiness.

**Next S237:** Full multi-process service fault-injection orchestration with lost ACK transport, broker restart, and atomic recovery evidence auditing.
