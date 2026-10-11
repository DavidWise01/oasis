# ROOT0 P4.56 — Request-role separation (2026-10-10)

**29/29 assertions PASS**, Node 22 TLS localhost regression, latest 730.106 ms. P4.56 integrated server uses two independently generated Ed25519 request signing keypairs: ordinary controller may send OBSERVE, COMPARE, LATEST, but ROTATE must be signed by dedicated rotation requester. Administrator's signature on rotation policy is separate from the rotation request authorization. TLS CA peer authentication, current fingerprint allowlist and policy epoch remain required. Regression confirms controller signature denied for ROTATE, rotation requester denied for LATEST, overlap/revocation/rogue cert, forged request, nonce replay, rollback/fork, and persistence across actual SIGKILL.

**Not a separate host:** all keys and service generated on same test machine; crypto role division does not guarantee separate human or physical custody. Hosted CI not checked. Production admin key custody, second-host deployment and authoritative rollback guard unverified.

Commit of `p456_role_guard.mjs` demonstrates role-verification rule; full tested `p456_server.mjs` and `test_p456.mjs` live in ZIP, not synchronized to GitHub. ZIP SHA256 `62b1b34e64b79033e057708eedbb8a3d895c88d5071d4b1789d83087fb5786cc`. Percentage held **14/20 = 70%**, because independent-host custody is not yet complete; this is a prototype milestone indicator only.

Next P4.57: integrate and commit P4.56 live server/test into GitHub, test separate role private-key custody, and network-separated anchor with external rollback witness.