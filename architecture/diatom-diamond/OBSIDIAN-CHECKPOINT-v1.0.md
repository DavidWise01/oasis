# OASIS / KET `{{i & dd}}` — Obsidian Checkpoint v1.0

**Status:** Additive software prototype, not quantum hardware or a hardened production signing service. Original frozen v0.7 source, v0.8 simulator, and v0.9 obsidian-core logic are byte-for-byte unchanged.

## Provenance and geometry

- Frozen dual5 floor: five passes of `UUDDLRLRBASS` along each of the forward and reverse rails, 60 steps per rail (120 across both). The base is the user-defined symbolic language with letters `AaaA` through `ZzzZ`, canonical arbitrary-length decimal integers, and supported punctuation/symbol tokens.
- v0.8: finite classical complex statevector simulator, with an explicit QFT plus controlled modular addition generating entanglement for finite 2..16 local registers; it does not assert entanglement produced by permutations alone.
- v0.9: a faceted OBSIDIAN-style black-glass core visualizes source identity, rail witness, and isotropic noise state. Natural obsidian is volcanic glass, not a periodic crystalline lattice.
- v1.0: two cryptographic signers, authenticated checkpoints, append-only file stages, and crash-recovery checks. This layer does not change the legacy geometry or gate model.

## Signed checkpoint format

Each checkpoint consists of three separately durable files named `000000000001.prepare.json`, `.commit.json`, `.finalize.json`, all retaining identical record IDs. The record commits to `(version, seq, prior_record_id, source tokens, noise, parent, generation, verified floor hash, core witness, output digest)`. The checkpoint ID is SHA-256 over a canonical JSON encoding of the record with domain tag `OASIS-OBSIDIAN-RECORD-v1.0`. Each stage has its own domain-separated hash `SHA256(['OASIS-OBSIDIAN-STAGE-v1.0',stage,record_id])`. **Both distinct Ed25519 keys sign every stage digest.** The SHA-256 chain links the prior committed record to the next.

On-disk writes use: create exclusive temporary file with 0600 mode → write and file fsync → link the temporary file exclusively to immutable stage name → unlink temporary file → fsync directory. Changes to already-written stage files are rejected, not overwritten. The approach is a local reference implementation; complete hardware/OS power-loss durability and multi-process locking have not been demonstrated on every platform.

## Recovery semantics

1. `PREPARE` with no signed `COMMIT`: never advance state; quarantine the prepared file explicitly. Do not synthesize commit.
2. Dual-signed `COMMIT` without `FINALIZE`: accept as committed after verifying both signatures, floor and core computations, chain linkage; recover finalization only with the two signing keys available.
3. Dual-signed `FINALIZE`: accept as finalized, including when the process crashes before returning to the caller.
4. Corrupt signatures, digest mismatches, removed intermediate stages, floor mismatch, chain gaps, and extra files: fail closed.
5. Rollback protection requires an **independent external trust anchor** (`anchorHead`, ideally paired with `anchorSeq`); hashes in a local directory alone do not prove a complete history. Concurrent writers require external single-writer fencing. Quarantine moves are intentional administrative operations; they are not append-only in the strict immutable-store sense.

The two demo Ed25519 keys are generated in the same process solely for testing. They provide two *distinct keys*, **not** organizationally independent or physically separated witness custody. No private keys are included in the demo receipts, viewer, source package, or Git commit. Production deployment would require secure key provisioning, segregated trust, filesystem ACLs, backup/retention policy, key rotation, and additional fault-injection testing.

## Reproduce (Node 22+)

```sh
node frozen/dual5-floor-v0.7/benchmark.mjs
node i-dd-obsidian-v0.9/obsidian-benchmark.mjs  # if using bundled v0.9 folder
node obsidian-checkpoint-benchmark.mjs
node make-demo.mjs
```

The first suite validates the frozen floor, the second validates v0.9 core/noise, and the third validates v1.0 signing and crash recovery. The `make-demo.mjs` generates an unprivileged sample with two finalized checkpoints and one prepared-only crash stage; no private keys are exported. The standalone Three.js viewer includes a copy of the public demo fixture and may use browser WebCrypto for Ed25519 verification in secure contexts. In restricted browser environments the viewer shows **UNVERIFIED** rather than claiming a signature check succeeded.

## Security limitation and quantum language

This is deterministic cryptographic audit machinery around a **classical quantum-state simulation**. It does not implement a hardware quantum processor, certify physical entanglement, or guarantee production-grade crash consistency, distributed consensus, or malicious-host resistance. A successful benchmark demonstrates code properties within the tests; not security of the deployment environment.