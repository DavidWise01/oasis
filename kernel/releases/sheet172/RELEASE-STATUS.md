# SHEET 172 — Merkle-Proven Signed Policy Anchor

Focused tests run locally: **24/24 PASS** (`node gate172.js`), inherited SHEET 171 **21/21 PASS** (`node previous/gate171.js`).

New `merkle172.js` computes domain-separated SHA-256 leaf and internal hashes, verifies inclusion paths against a supplied source-signed root with explicit leaf index and count, rejects malformed paths and duplicate batch indices. Test integration checks source Ed25519 signature and 2-of-3 witness certificate prior to signed anchor advancement. The anchor rejects generation replay and survives reopen.

Executable conversation archive `SHEET172-merkle-proven-anchor.zip`: 18,311 bytes, SHA-256 `497670bd55b78b9857e21c4713bb8025afc591fbe107ed96cfbc581e256a2d92`. Includes runnable 172 sources and preserved 171 baseline. This GitHub commit is the release record; executable sources reside in the ZIP.

**Verification boundary:** This release does NOT provide independently hosted authority or new mTLS transport, Merkle consistency/append history proofs, full-stream completeness, actual live SHEET 166 source/target recovery integration, independent storage hardware, or cross-host partition testing. The complete historical regression suite was not rerun. The checked Merkle root is source-signed in fixture data and not independently obtained from a production source.

Next SHEET 173: mTLS-authorized remote anchor and signed Merkle consistency / contiguous recovery cursor proof.
