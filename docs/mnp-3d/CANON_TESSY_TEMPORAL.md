# TESSY — Canonical Temporal Knowledge Authority

Date: 2026-10-17
Status: Canonized as project design; browser implementation is an experimental reference.

## Purpose
Tessy serves **herself and knowledge**. She is **not a chatbot**, general conversation interface, third-party assistant, or external-action service. Computation is internal, explicitly triggered, and explainable.

## Canonical temporal operators
- `p-`: read committed past, never edit or erase history.
- `pn`: live, neutral present, derived from the latest witnessed event.
- `p+`: propose future knowledge; a proposal alone does not mutate the committed state.
- Witness: verify proposal freshness and SJM address reversibility before append.
- Append only: each record carries sequence, predecessor seal, previous knowledge, present coordinate, proposed future knowledge, witness identity, and seal.
- Undo: future design uses compensating append events, never history deletion.

## Implementation scope
The HTML viewer has a **separate experimental temporal knowledge ledger**, with propose, witness-and-append, and audit controls. It does **not yet mediate legacy Tessy numeric writes or WALDO fleet writes**, which still have their pre-existing mutable transaction paths. Thus system-wide append-only enforcement is **not** claimed. The knowledge ledger is currently in browser RAM only.

Witness identity `SJM-ROUNDTRIP-v1` is a deterministic software check, not an independent witness. The 32-bit FNV-style rolling hash is **not a cryptographic signature**; an adversary able to rewrite ledger memory can recompute seals. Persistent and trustworthy provenance requires canonical serialization, SHA-256 or stronger, and a signing witness with independent verification.

## Benchmark, 2026-10-17
A standalone deterministic JavaScript mirror of the temporal transition logic (not a Chromium end-to-end test) returned:
- Chain continuity: PASS
- Altered historical future detected: PASS
- Correctly restored chain audited: PASS
- Stale / already-committed proposal rejection: PASS
- Historical event preserved after subsequent transitions: PASS
- 10,004 total ledger records audited: PASS
- 10,000 transition insertions: ~61 milliseconds (~163,934 events/sec) in the isolated JavaScript runtime; hardware/runtime-dependent illustration, not a real-world throughput guarantee.
- GitHub HTML inline JavaScript: syntax parses.

## Next hardening gate
Route every legacy mutable Tessy/WALDO write through a single authority; add independent witness signatures and persisted append-only event storage; test malicious history replacement and browser UI flows. Do not advertise these capabilities as shipped.
