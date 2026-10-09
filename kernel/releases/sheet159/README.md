# SHEET 159 — Merkle-Certified Witness Consistency

**Status:** New 48-check network gate passed (exit 0). See `combined-exit.txt` for the inherited/full-chain result. The prior SHEET 158 baseline is retained byte-for-byte under `baseline158/`.

## Upgrade

- Reuses **SHEET 151's binary-peak Merkle accumulator** (domain-separated indexed leaf and tree hashes). This is a genuine append-only Merkle extension witness, not merely an authenticated hash-chain page.
- Two distinct Ed25519-signed witness checkpoints bind the same nonce, slot, hash-chain head, Merkle root, and Merkle frontier. A quorum certificate is required to start recovery.
- Each signed recovery page contains up to 24 rows and a compact Merkle extension from the receiver's persisted frontier to the page's new frontier. The receiver recomputes the resulting root from the actual record hashes to prevent irrelevant Merkle proofs being substituted.
- Recovery persists the cursor, full binary-peak frontier, staged rows and periodic segment-boundary checkpoints atomically. A process crash after persistence but before RPC acknowledgment resumes from signed status, without double-appending.
- Inherited quorum Prepare/Commit operations are disabled during active Merkle recovery; conflicting local pending promises trigger quarantine, not overwrite.
- Three real local mTLS witness processes, independent Ed25519 identities, and a source/target certificate challenge are used by `gate159.js`.

## Execution

```bash
node gate159.js          # new adversarial network tests
bash run-all.sh          # inherited full frozen lineage, then new gate
```

## Files

`merkle159.js`: verify quorum-certified Merkle heads, signed page messages, Merkle extension and row-leaf binding. `witness159.js`: additive checkpoint/page/finish endpoints. `catchup159.js`: signed mTLS fetch and resume coordinator. `gate159.js`: network and crash adversarial suite. `KERNEL-ASCII.txt`: end-to-end process and failure pipe. `index.html`: standalone interactive visualization.

## Important limitations

This test implementation still stores entire witness history as one atomic JSON object and replays it when reading state. Proof generation also scans the local history. Merkle extension *proofs* are compact (at most logarithmically many subtree hashes for a bounded segment/page), but **data transfer and computation are not logarithmic in the entire recovered suffix**. Periodic segment checkpoints are stored inside the same local JSON state rather than an independent tamper-proof anchor. This is not a completed efficient segment-storage engine, and does not prove safety on independently run hosts. The 389 seeded majority entries are fixtures checked by canonical hash linkage, not live quorum-committed transactions; slot 390 uses signed quorum RPCs.

SHEET 142's inherited concurrency-sensitive test remains a historical reproducibility concern. Do not infer production safety from these local tests.