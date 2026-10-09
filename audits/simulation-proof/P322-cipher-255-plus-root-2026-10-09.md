# ROOT0 P3.22 — canonical cipher count correction (2026-10-09)

User correction: **not 208 cipher; 255 with 1 root**. Canonical interpretation for current implementation: one pinned root at index 0, plus 255 nonroot cipher positions indexed 1..255, total 256 addressable positions. Earlier 208-position implementation or validation is preserved in historical revisions but its count is superseded; it must not be advertised as exhaustive evidence for the 255-position cipher.

New files: `p322_cipher_contract.mjs` and `test_p322.mjs`. Local Node v22.16.0 execution PASS: all 256 canonical two-character hexadecimal index representations round-trip, 255 forward and reverse ordering positions match, pinned 0 is separate, malformed indices rejected. Index encoding is a chosen serialization, not an assertion that the user's cipher operands are intrinsically hexadecimal.

**Boundary:** This is a count/addressing contract, not implementation or verification of 255 underlying cipher transformations. The P3.7-P3.21 Dyson/math code is retained untouched; existing 208-step tests remain historical, not current full-coverage cipher tests. Next target: define the authoritative 255 operator sequence or stage generator, then test complete forward/backwards operator semantics and join the full P3.20/P3.21 chain.
