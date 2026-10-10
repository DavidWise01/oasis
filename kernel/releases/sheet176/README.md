# SHEET 176 — Transactional Sapphon/Cortex Recovery Prototype

Local run: S176 20/20 PASS, inherited S175 26/26 PASS, S174 20/20 PASS, S173 22/22 PASS (88 focused checks total).

New kernel writes hash-linked prepare and commit records to one fsynced WAL after S175 signed route/capability verification. Only matching committed records become visible. Nonce replay is rejected, a stale writer is refused, and a torn or interrupted prepare quarantines recovery.

Full self-contained executable archive: `SHEET176-transactional-sapphon-cortex.zip` (36479 bytes), SHA-256 `edbcc73b17ae8a33816caee7b57590c0a0f5f8667f5445c1ce1e008f06e3f23e`. ZIP includes original test runner and complete S175 predecessor source.

GitHub's new source below is a dependency-layout port; the **exact tested layout is in the ZIP**. GitHub alone is not a standalone self-contained release because earlier predecessor implementations were published primarily in ZIPs.

Caveats: only one local writer, simulated exception after prepare rather than hard power loss, no atomic remote target-DB + WAL commit, no independently protected rollback floor, and no cross-host safety proof. An abandoned lock after hard kill requires operator action. No claims of exactly-once remote recovery.

Next SHEET 177: independently signed WAL head, crash-kill fencing, durable target-cursor reconciliation and evidence-bound rollback defense.
