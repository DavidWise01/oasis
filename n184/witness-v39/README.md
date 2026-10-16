# N184 v3.9 — Append-only gateway witness

This is an additive GitHub Pages module; earlier N184 v3.7 and v3.8 files are unchanged.

## Routes
- Observatory: `../`
- Original White Sun React VM: `../white-sun/`
- New witness page: `./`

## What works in code
- Same-origin VM iframe and origin/source validation on inbound `N184_PHASE_REQUEST` messages.
- Version 1 `N184_STATE` snapshots including phase, six port configuration records, and 60×40=2400 frozen lattice.
- Session-local hash-chain ledger with sequential indexes and SHA-256 over canonical JSON object insertion order.
- Export as JSONL and chain audit.
- Locally logged duplicate/replay attempt without forwarding it.
- New module added; prior pages not overwritten.

## Important limits
The previously existing White Sun receiver **does not send an ACK**, so the displayed ACK counter does not increase. This v3.9 page witnesses **transmission and requests**, not verified receipt by the React state machinery. The embedded original React controls are not synchronized into its internal app state; only the separately added overlay receiver consumes gateway messages. No browser smoke test, missed-message recovery, offline persistence, durable append-only backing storage, authenticated signing, or actual hardware port tests have been completed.

Future v4.0 should add a protocol ACK emitted by a new receiver layer, duplicate rejection on arrival, snapshot resume after reload, and an external witness checkpoint, while maintaining additive-only versioning.
