# KET Boundary 02 — benchmark and engine classification

Date: 2026-10-22
Source: `research/ket/boundaries/ket-boundary-02.html`
Original local HTML SHA-256: `bbdfd670d5d3b9333d34afe3a018d7725075743db89a56cfdc544852a80bceff`
Benchmark: Node.js 22.16.0, built-in `crypto.webcrypto` SHA-256; direct evaluation of unmodified core JS functions extracted from that HTML. The Chromium runtime blocked both file:// and localhost, so **browser UI was not benchmarked**.

## 120 sequential receipts (Z184 → Z400)

- Valid hash-chain verification: PASS, 120 entries
- Actual route: 29 hops, 30 addresses; full route preserved in source results locally
- Total average transaction latency: **18.825 ms**
- Median transaction latency: **21.200 ms**
- First: **5.069 ms**; last: **36.721 ms**
- Full 120-entry validation: **35.331 ms**
- Duplicate identity: **REPLAY**, **35.943 ms** (no new journal entry)
- Tamper entry #41 hops changed to 999: **HASH_MISMATCH at zero-based index 40**
- Final chain head: `5ef536da60d1abc726c18f9e4f41f89fba512defffda974d228bee3c66c32ad2`

These figures are a single machine/run, not stable capacity claims. Source currently revalidates the entire chain and reconstructs routes on every append, causing increasing latency and quadratic total work across a long sequence. The transaction process also serializes complete snapshots and depends on browser localStorage.

## Functional envelope

- 488 symbolic addresses, four roots, shortest-path BFS.
- Exact canonical 42-digit mirrored payload with `-+` delimiters.
- THREE GATES simulated evidence decisions, a 256-cell inversion/mirror address mapping.
- Append-only linked local receipt journal, duplicate identity suppression, storage revalidation, quarantine.
- **Not** a distributed consensus protocol, physical chip governance, legally binding restitution, or guaranteed exactly-once cross-system delivery.
- Matching hash only demonstrates internal integrity relative to provided data and an independently trusted digest. An attacker with write access can rewrite the whole local journal and hash it again.
- `validate()` authenticates the stored receipt bytes by chain continuity but does not independently establish whether a receipt's claimed evidence state was originally true. Therefore `HOLD` is scoped to the test's specified expectation and supplied evidence flags.
- Test harness cannot establish browser lifecycle reliability or external durability.

## Engine type

**A governed event-sourced transaction and provenance engine, with a toroidal symbolic router as its visualization.**

The event receipt is its fundamental output; routing resolves topology, the three gates decide whether to accept, and the hash-linked journal preserves accountable history. Its next natural production boundary is a **signed append-only ledger** with independent anchor, canonical serialization, crash-safe storage, idempotency keys, explicit transition table, per-hop evidence, and incremental or checkpointed validation. Retain the symbolic 488 / 256 / 16 / 8×3 overlays as pluggable adapters, not replacements for the receipt core.

`[[ BOUNDARY02 :: 120 TX :: VERIFIED :: BENCHMARKED :: EVENT-SOURCED PROVENANCE ENGINE ]]`
