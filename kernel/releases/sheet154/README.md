# SHEET 154 — Quorum-Admitted Finality / Anchor Admission Gateway

**Status:** new fault suite **40/40 PASS**. See `combined-exit.txt` and `combined-run.log` for the inherited test-chain outcome.

## Design

SHEET 153 uses a local finality file lock to sequence an anchor advance and a replicated authority completion. SHEET 154 adds an **independent quorum-held finality decision** that needs no coordinator-local file lock. Three finality processes persist and sign a `PREPARED → ANCHORED → FINAL` progression. A separate mTLS **anchor-admission gateway** is the only holder of the credential authorized to advance the frozen SHEET 151 anchor signer. It checks a 2-of-3 signed PREPARED certificate against the exact authenticated physical receipt, journal inclusion proof and resource checkpoint. The signer retains its own durable high-water history.

In each finality replica, `PREPARED` verifies the existing SHEET 148 majority-signed grant, SHEET 153 physical record and receipt, S151 checkpoint signature, inclusion path and the live independent anchor head. `ANCHORED` verifies the exact signed checkpoint movement and original 2/3 prepare votes. `FINAL` additionally verifies **two independently signed SHEET 147 completion journals**, including their own majority-signed proposal votes and chained row history. A stale coordinator can replay the same intent only; competing intents are rejected.

## Fault test evidence

`node gate154.js` creates an inner anchor signer, a gateway and three finality replicas, all as separate real mTLS processes. It writes a real SHEET 153 segmented journal record and constructs test-fixture majority-signed SHEET 147 grant and completion journals. It checks direct TLS gateway bypass, forged votes and receipts, Merkle substitutions, a gateway killed after inner checkpoint fsync but before acknowledgement, restart of finality replicas with their durable PREPARED/ANCHORED states, forged completion proof, rollback and majority partition. The gate has **40 checks**. The underlying physical record remains at count one throughout reconciliation.

**Security qualification:** The signed authority journals in the *new SHEET 154 gate* are generated from synthetic test keys, not fetched from separately running SHEET 153 authority processes. The inherited SHEET 153 regression suite exercises its own live resource and authority processes. This is **not** a fully integrated cross-host consensus test. All SHEET 154 processes ran on one physical host, with separate persistent state directories. The protocol currently supports one immutable finality slot; later transaction rotation, independently operated hosts and full SHEET 153 live-journal wiring remain future work. Its signatures prove authenticated observations in this test model, not atomic transactions or independent physical disk reliability.

## Run

```bash
node gate154.js
bash run-all.sh
```

The full `run-all.sh` copies the frozen SHEET 153 tree to a temporary directory before executing the original lineage suite and then SHEET 154 tests. It does not modify the preserved prior kernels.

For the full process architecture, key domains and 42-stage pipeline, see `KERNEL-ASCII.txt`. The SVG fault viewer is `index.html`. For reproducibility, inspect `new-test-report.json`, `combined-run.log` and release manifest.

## Next target

SHEET 155 — Live SHEET 153 majority journal wiring and multi-transaction quorum-slot rotation with external rollback floors, tested across separately networked containers or hosts when available.