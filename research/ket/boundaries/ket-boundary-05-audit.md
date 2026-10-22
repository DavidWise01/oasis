# Boundary 05 — Independent Witness Verification

2026-10-22. Implementation: `research/ket/boundaries/ket-boundary-05.html`.

## Purpose

Read-only verifier for Boundary 04 exports: receipt journal JSON and signed checkpoint JSON. The user supplies a previously trusted SHA-256 pin of the public JWK from a separate channel. The verifier uses the exact receipt schema and route logic from Boundary 04, not an independently standardized protocol.

## Tests

Node.js 22.16.0 WebCrypto, direct evaluation of the same core JavaScript embedded in the HTML.

- 120 sequential synthetic receipts accepted.
- 1 authentic checkpoint accepted after full hash-chain and route audit.
- 1 incorrect trusted-key pin rejected (`TRUST_PIN_MISMATCH`).
- 1 truncated journal rejected (`TRUNCATED`).
- 1 altered receipt rejected (`JOURNAL`).
- 1 modified signature rejected (`SIGNATURE`).
- 1 duplicate packet ID suppressed (`REPLAY`).
- **126/126 assertions passed.** Route Z184→Z400: 29 hops.

## Trust model and limitations

- An independent key pin is mandatory; importing only the anchor's public key would allow a locally forged anchor+key to appear authentic.
- The pin covers public-JWK fields `{crv,kty,x,y}` in fixed JSON order. Trust in the pin's original enrollment is external to this app.
- The verifier confirms the signed **checkpoint prefix** and tracks later **unanchored entries**. It does not mistake those later entries for signed history.
- The app is read-only and has no access to external deliveries, actual legal authorization, or physical truth of claims.
- Browser UI and IndexedDB multi-tab/crash correctness remain unverified in this execution environment. This is Node.js core validation, not an end-to-end concurrency test.
- Current Boundary 04 stores its private signing JWK locally. Theft of this key defeats future signature security; use independently controlled signing in any production design.
- Boundary 04's receipt ID replay treats an existing ID as REPLAY even if a subsequent request's payload changes; future work should reject conflicting reuse of IDs.
- No guaranteed exactly-once external side effects.

## Next boundary

Independent key custody; conflicting duplicate payload rejection; real-browser multi-tab IndexedDB harness; external delivery idempotency and acknowledgments.

`[[ BOUNDARY05 :: INDEPENDENT WITNESS :: SIGNATURE :: TRUST PIN :: 126/126 ]]`
