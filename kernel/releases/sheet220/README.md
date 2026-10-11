# SHEET 220 — Mandatory Provenance in the Local Socket Writer

**Executed:** new S220 gate 16/16; S219 17/17; S218 15/15; S217 9/9; S216 13/13 — **70/70 focused checks passed**. The socket handler dispatches all append requests through the signed-ledger `FencedWriter`, excluding caller-controlled WAL paths and input payloads. Test cases reject missing registrations, tampering, stale ownership, replay and unauthorized request fields. This is a local gate, not a distributed execution proof.

**Release:** `SHEET220-service-provenance-gate.zip`, 69 files, 94,525 bytes, SHA256 `8b8650c51427c4008b22a5d2d22682c2c1bf7c3797017e634a1e225ae7090426`. Contains runnable `gate220.py`, `service220.py`, S219–S216 regression gates and all inherited source.

**Limitations:** direct legacy writer invocation remains possible with filesystem permission; socket mode 0600 alone cannot block same-UID bypass. No cross-store atomicity, end-to-end mTLS test in this gate, or physical host separation. Next S221: enforce OS service UID isolation and live floor-target regression through the new service.
