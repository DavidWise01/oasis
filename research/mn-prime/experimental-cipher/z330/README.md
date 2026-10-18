# Z330 — Tritrinilium (Ttn): signed recovery and revocation

**Status:** MN PRIME / OCTAVIA Layer 1 symbolic software candidate. No physical element discovery. Name constructed from IUPAC digit roots tri-tri-nil-ium; symbol Ttn avoids earlier Tbn collision.

## Mechanism
- Full optional Cr24 distinct address space: 24! rank indices.
- Each segment contains sequential ID, signer key ID, parent digest, index list, and Ed25519 signature over canonical JSON.
- Key rotation A->B requires a signed rotation certificate from A, effective at segment 1.
- Incomplete appended segments are discarded; recover only to the last complete chain with trusted terminal digest.
- A trusted revoked-key set rejects chain segments signed by revoked keys.
- Keep frozen KET and 5/3/1 hierarchy separate from RGB (3,1,2) occupancy.

## Measured local evidence
Ran `python test_z330.py` on 2026-10-18: **20/20 PASS**. Includes genuine signatures, successful authorized rotation, complete chain, partial segment rejection, rollback/truncation/reorder detection against trusted tip, invalid index, tamper and rogue signer rejection, revocation, and distinct names.

## Limitations
Test-only deterministic private keys; **never** use them for production signing. No production trust store, signed revocation list, timestamping, trusted clock, key management, external audit, or protected storage. The interrupted state is modeled by an incomplete in-memory segment and verified recovery prefix, not a full crash-durable database implementation.

Next Z331: external anchor interface and explicit rollback/revocation epochs, preserving immutable baseline.
