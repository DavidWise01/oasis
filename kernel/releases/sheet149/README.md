# SHEET 149 — Replica-Enforced Resource Receipt Authentication

**Status:** Tested local reference build. **64/64 new tests passed**. The inherited SHEET 148 chain (**1,114 checks**) passed in an earlier integration run with the first 62 new checks. The final **64 new checks** passed separately after the replay-verification additions. The latest full combined rerun timed out near completion and is **not** certified as a fresh 1,178/1,178 pass. This does not cure the previously observed intermittent SHEET 142 test.

## Why it exists

The SHEET 147 replica allowed a leader to complete a pending grant with a syntactically valid `receiptHash`. SHEET 148 verified resource signatures in the coordinator bridge, but a malicious leader could bypass that bridge. SHEET 149 adds hard validation to *every replica* and to all three stages: `/prepare`, `/commit`, and journal replay. A `COMPLETE` now carries the **full resource-signed receipt** and its hash.

## State transition

`BEGIN -> 2/3 certified grant -> resource-signed durable write -> COMPLETE(receipt, receiptHash) -> replica verification -> 2/3 certified completion`.

Every replica independently checks the pinned resource Ed25519 key, domain-separated `S148:RECEIPT` signature, txid, resource ID, digest, epoch, grant head, record sequence/hash, and exact hash of the signed receipt. A hash-only completion is rejected, even if an adversarial test supplies two well-formed replica vote signatures. Journal replay rechecks the resource signature, so corrupted or forged receipts cannot be laundered through a restarted replica's state file.

## Files

- `replica149.js` — hardened networked replica, preserving SHEET 147 election/log protocol message domains but using its own `oasis.sheet149.replica.v1` state schema.
- `bridge149.js` — complete resource receipt transport into the replica quorum (maintains SHEET 148 grant interface).
- `gate149.js` — full local TLS multiprocess fault gate, including malicious leader, crash-after-durable-write, handoff, partition recovery, and tampered journal replay.
- `baseline148/` — byte-for-byte copy of the SHEET 148 release directory; never altered.
- `index.html` — interactive SVG architecture and scenario panel; visualization data is explanatory, not a live service monitor.
- `KERNEL-ASCII.txt`, `SHA256SUMS`, `release-receipt.json`.

## Run

Node.js 22 and OpenSSL are required. From the unpacked `sheet149` directory:

```bash
node gate149.js
bash run-all.sh
```

The new gate creates temporary self-signed TLS test credentials, spawns three authority replicas and one resource process, injects forged and stale data, and destroys the temporary secrets. These keys do not authorize anything outside the test.

## Security and scope

- A trusted resource's **private signing key** is assumed uncompromised. A compromised resource signer could sign fabricated writes; cryptographic authentication alone does not prove the resource performed an honest physical operation.
- This is majority agreement for crash/replay/invalid-input tests, **not proof of Byzantine agreement**. Two colluding signers can still influence quorum history and availability.
- The three replicas and resource are real TLS processes on a single test host, not independently operated machines.
- New replica durable state uses a new versioned schema. No automatic historical migration from a SHEET 147 state file is implied.
- Global distributed linearizability, external independent custody, production deployment, and historical SHEET 103 parity remain unverified.
- SHEET 142 has had intermittent timing-sensitive inherited concurrency failures. A single full-suite pass does not prove its repeatability.