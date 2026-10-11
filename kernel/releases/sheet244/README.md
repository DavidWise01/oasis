# SHEET 244 — mTLS Floor ACK-Loss Simulation

**Verified test runs:** S244 32/32; S243 39/39; S235 15/15: **86/86 PASS across three separate suites**. Original S176 Node writer and live target/floor mTLS service are used. Floor persisted an Ed25519 ACK, the S244 client adapter intentionally discarded the response, and `/status` recovered the exact original. Duplicate floor `/attest` returned the same receipt and broker authorized exactly one generation. S243 triple-process SIGKILL and S235 broker crash suites passed separately.

**Release ZIP:** SHEET244-mtls-ack-loss-simulation.zip, 59 files, 83,292 bytes, SHA-256 `750209a8fc77aec1f5b97e9962efb97f8dc68ccaf892f82280c6bb325fbf8fef`.

**Limitations:** Simulated ACK delivery loss at client boundary, not a real packet-filter or multi-host partition. No physical power-loss or cross-store atomicity proof. Progress remains **90% (9/10 local milestone demonstrations)**, not production readiness. Next S245: real TCP proxy or netns partition and reconnection, independently persisted signed floor ACK.
