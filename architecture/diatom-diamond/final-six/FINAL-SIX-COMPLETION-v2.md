# OASIS/KET — Final Six Completion, authenticated durable OBF2 v2

**As of 2026-10-14.** Single independently successful GitHub Actions integration run:
https://github.com/DavidWise01/oasis/actions/runs/38590542771

## Updated decision

**5 of 6 acceptance gates meet their tested scope. Production deployment still HOLD.**

| Gate | Outcome | Evidence |
|---|---|---|
| 1 — original `{{i}}` identity | PASS | 42 coordinate-distinct addresses, 8 views, all 2,688 directed view routes preserve source identity, `0` glyph collision avoided. |
| 2 — `{{d}}` reversible carrier | PASS | Previous final-six suite: 42 addresses recover through every source/target view pair. |
| 3 — ASTROPHAGE OBF2 Rust/WASM transport | PASS | Original frame 444 bytes, exact reconstruction in native Rust and WASM. v2.5 23.2 KB balanced WASM cross-checked in current run. |
| 4 — sender identity/authenticated provenance | **PASS in implemented scope** | Signed **Ed25519** sender/event/frame envelope. Receiver pins trusted sender public key; invalid, missing, altered and wrong-key signatures rejected. An authenticated change with reused event ID is rejected as a conflict. |
| 5 — crash/restart durable receipt | **PASS in implemented scope** | Append-only, SHA-256-linked receipt journal, `fsync` *before* ACK, idempotent duplicate classification, crash after durable commit and before ACK, restart and replay -> one receipt, partial uncommitted tail discarded, mid-log hash mismatch fails closed. |
| 6 — end-to-end independent-device stability | **PARTIAL** | 12 concurrent authenticated localhost TCP clients, all stored separately, plus corruption rejection and exact WASM parity. **Not** verified over two separate physical devices, network jitter/loss, or authenticated return channel. |

GitHub run independently passed the unchanged v2.1 OBF2 baseline (4,633 assertions) and executed 7 focused new acceptance checks with `FINAL_NEXT_RESULT = PASS_WITH_DEPLOYMENT_GAP`. Original frozen v0.7 SHA256 verified as `47d4c89ac8155b9470852e0e23d2c059ad087eedc2b7949632a9431b5792fd4b`. No frozen `{{i}}`, `{{d}}`, KET, or OBS source was changed.

## Changed software

- `final-six/secure-relay.mjs`: strict envelope fields `{v,sender,id,frame,sig}`, canonical signature domain `OASIS-SIGNED-OBF2-v1`, trusted-key allowlist, bounded TCP requests, OBF2 CRC and two-rail validation, persistent hash-chained journal.
- `final-six/secure-relay.test.mjs`: generates temporary keys on each run, proves forged/unsigned/altered/replayed messages are rejected or classified correctly; crashes receiver after `fsync` and before ACK; verifies recovered journal; tests 12 concurrent clients and actual v2.5 balanced WASM codec bytes.
- `.github/workflows/oasis-final-six-completion.yml`: rebuilds WASM from unchanged Rust v2.4 source, checks frozen hash, runs identity/protocol regressions and new focused acceptance.
- Earlier numerical optimization and 3 WASM variants remain intact; no performance claims made for the security layer.

## Precisely scoped delivery semantics

An **APPLIED** receipt means a particular authenticated event frame was committed to this receiver's *single-writer local journal*. A repeated identical `sender+eventId` returns **DUPLICATE** and the same stored receipt. A different valid frame with the same `sender+eventId` returns **CONFLICT**. This provides idempotent journal commits with at-least-once retry, *not exactly-once execution of arbitrary downstream effects*. Neither outbound ACKs nor TCP channels are authenticated by this layer: malicious network intermediaries remain a concern, and the public key must be provisioned over a trusted path.

The journal hash chain detects ordinary corruption or alteration **if an attacker cannot recalculate/replace the whole chain**; it is *not* a signed, tamper-proof audit ledger. This reference implementation assumes one writer per journal and does not manage multi-process file locking, key rotation, secure key storage, or external application effects.

## Why the sixth gate stays partial

The test's sender and receiver ran in different OS processes but shared one machine. This proves real local TCP behavior, not WAN behavior, independent clock conditions, or failure on two physical devices. A true sixth-gate PASS requires a real second endpoint, trusted key exchange, a protected two-way channel such as TLS or VPN, and one controlled authenticated send / crash / resend under actual link interruptions.

### Next single necessary acceptance

On two independent hosts: provision sender's public key securely, start the relay behind authenticated encrypted transport, send canonical ASTROPHAGE OBF2, disconnect/kill receiver immediately after an `fsync`-confirmed commit but before ACK, restart, resend, observe one original receipt and `DUPLICATE`; run a small concurrent batch. Mark gate 6 PASS only if those exact observed outcomes hold.

**No additional speculative physics claim:** this verifies deterministic, classical message processing, not entanglement, elimination of propagation delays, or source truth. Source authentication is not factual verification.
