# Boundary 06.5 — Corrected freeze candidate

Source `research/ket/boundaries/ket-boundary-065.html`
SHA-256 of local source: `21ec524739e65d55bc82983ea6ef4b6dda653ecc4835867c838546477f5911b2`
Test environment: Node.js vm + WebCrypto; **15/15 targeted assertions PASS**.

Changes from Boundary 06:
1. Canonical requestFingerprint(id,from,to,token,expected,actual) for both legacy in-memory path and IndexedDB writer.
2. Every new receipt stores requestDigest.
3. Reuse of ID with same original request is REPLAY; conflicting request is ID_CONFLICT and appends nothing.
4. verifyFrozenJournal() checks full hash chain then requires a signed independent checkpoint and verification key. Without them returns MISSING_TRUSTED_ANCHOR. A truncated chain relative to that checkpoint is rejected.
5. New IndexedDB origin database name separates the revised candidate from B06's old persisted records.

Tests: token digest; 488 bounds; 29-hop route; mirror index 201; digest recorded; replay; ID conflict; conflict nonappend; 120 hash-linked receipts; valid signature; frozen journal; missing anchor fails closed; truncated journal rejected; changed receipt rejected; wrong-key rejected.

Important: An independently **trusted** checkpoint and public key are necessary. If the journal and signature/key are both under attacker control, they can be replaced together. This harness does not demonstrate real tab concurrency, browser IndexedDB recovery, or cross-system exactly-once effects. Browser testing **NOT RUN**.

Status: source fixed and tested; original B06 preserved; no invented external certification stage.
