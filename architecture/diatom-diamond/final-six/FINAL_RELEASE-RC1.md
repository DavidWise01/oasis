# OASIS — FINAL RELEASE CANDIDATE (RC1)

**Date:** 2026-10-14  
**Release:** OASIS KET / ASTROPHAGE / OBF2, frozen-core RC1  
**Acceptance:** 5 of 6 production gates completed; two-physical-device network acceptance requires an observed field run.  
**Decision:** **Software release candidate FROZEN; production deployment HOLD** until gate 6 has real two-device evidence. Do not represent 6/6 as complete.

## What is frozen

The three-track KET mathematics, coordinate-distinct 42-token `{{i}}` register, eight views (2,688 directed address-view combinations), six-node graded chain, `{{d}}` reversible carrier, OBS dual-rail five-pass permutation, and OBF2 wire format. No original frozen source files have been edited.

## What works and how it is checked

1. **Identity**: 42 unique source identities, eight views, duplicate visible glyphs stay distinct. PASS (prior final-six CI).
2. **Representation**: 4/3 diamond losslessly recovers every coordinate identity. PASS (prior CI).
3. **Communication**: 214-byte canonical ASTROPHAGE payload → 444-byte OBF2 dual-rail frame → exact Rust native and balanced WASM recovery. PASS (prior CI).
4. **Source authentication**: Ed25519 sender signature plus TLS 1.3 authenticated encrypted channel; wrong signer/unsigned inputs rejected. PASS in local test.
5. **Durability**: One-writer append-only, fsync-before-ACK journal; retry after abrupt server exit returns DUPLICATE with one durable receipt. PASS in local test. Arbitrary third-party side effects are not exactly-once.
6. **Independent endpoints**: TLS server and client software tested as different local processes; independent physical computers, protected LAN/VPN and failure/retry still await deployment. PARTIAL / NOT FIELD VERIFIED.

## Software acceptance added at final pass

- `architecture/diatom-diamond/final-six/remote-mtls.mjs`: authenticated two-device launcher using Node built-in TLS 1.3/mTLS plus signed OBF2 envelope and durable journal. Uses a private trusted CA and trusted signer public key.
- `.../setup-keys.mjs`: creates a private CA and separate short-lived server/client certs **at deployment time**, never part of release archive.
- `.../remote-mtls.test.mjs`: five *focused local* checks; wrong client TLS certificate, forged Ed25519, durable duplicate ACK and killed receiver recovery.
- `TWO_DEVICE_SETUP.md`: copy-and-run commands and final field signoff checklist.

## One simple metaphor

`{{i}}` is the **name printed on each LEGO part**. OBF2 is the **packing system** that can rebuild two views of the same note to spot damage. Ed25519 is the **sender's unique signature**. TLS is the **locked delivery truck** between two computers. A fsynced receipt journal is the **notebook that remembers delivered packages after a power outage**. None of these by itself proves that what the sender wrote is factually true.

## Boundaries

Use only on a private LAN or authenticated VPN with firewall limits; this is a single-writer reference deployment, not a multi-tenant public Internet service. Cryptographic certificates expire and require controlled storage and rotation. Signatures do not prove scientific claims, and a duplicate receipt does not ensure every external side effect happens exactly once. CRC32 detects accidental corruption; it is not authentication. Zero physical network latency and quantum entanglement are not asserted.

## Final action

On two **different physical machines**, run the steps in `TWO_DEVICE_SETUP.md`, note an APPLIED ACK, disconnect/restart receiver, and resend the **same event ID** to confirm DUPLICATE with the identical receipt. Once actual evidence is observed, update the field acceptance record to PASS; until then, **production remains HOLD**. Do not create another artificial test cycle.