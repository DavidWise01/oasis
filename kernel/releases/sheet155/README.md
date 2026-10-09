# SHEET 155 — Live Authority Journals, Multi-Slot Finality & External Rollback Floor

**Status:** See `combined-exit.txt`, `combined-run.log`, and `new-test-report.json` for reproducible execution results. This is a local development prototype, not a production distributed consensus service.

## Upgrade over SHEET 154

SHEET 154 held exactly one immutable finality transaction and used cryptographically signed, synthetic SHEET 147 authority-journal fixtures in its new gate. SHEET 155 retains all frozen predecessor code under `baseline154/`, and adds:

- **Live authority verification:** every finality replica requests `S147 /journal` from actual TLS-protected authority processes, verifies `S147:JOURNAL` signatures, checks each chained proposal, checks 2-of-3 distinct `S147:PREPARE` signatures per row, and demands two matching journal heads. Both BEGIN and COMPLETE are read from live replicas.
- **Ordered multi-slot finality:** separate append-only per-replica events track `PREPARED → ANCHORED → FINAL` across a sequence of slots. The next slot must be exactly previous+1.
- **Independent signed rollback floor:** a separate TLS signer stores a chain of quorum-certified FINAL slots and signs its current head. Each new slot binds its predecessor floor head; a restored old replica is detected against the externally retained floor.
- **Gateway-fenced checkpoint advancement:** the only mTLS identity authorized by the frozen checkpoint signer remains the gateway. Its new version checks both the 2-of-3 signed PREPARED certificate **and** the current independent rollback floor before asking the signer to advance.
- **Adversarial gate:** tests genuine elections from alternating leaders, physical segmented writes, multiple completed finality cycles, a restarted finality replica, wrong signatures, floor rollback/tamper, and denial of finality with only one live authority replica. The partition fixture includes a fourth *pending* physical write which is explicitly not counted as finalized.

## Main files

- `finality-replica155.js`: independent signed journaling, slot progression, live authority majority reads.
- `anchor-gateway155.js`: 2-of-3 signed PREPARED gate and pinned external floor.
- `floor155.js`: durable external high-water chain and finality vote verification.
- `quorum155.js`: multi-slot coordinator requests, without possession of the inner signer credential.
- `gate155.js`: real subprocess/TLS fault gate; ephemeral keys and state under a temporary test directory.
- `KERNEL-ASCII.txt`: complete 48-stage pipeline, source-of-truth boundaries and failure matrix.
- `index.html`: standalone SVG fault-scenario dashboard.

## Reproduce

```sh
node gate155.js
bash run-all.sh
```

The combined runner clones the **frozen SHEET 154 baseline** to a temporary directory before running the full inherited test chain. It then runs the SHEET 155 test gate. You need Node.js 22+, OpenSSL and Bash.

## Explicit limits

All mTLS services ran as separate processes on a **single physical host**, not independent fault domains. SHEET 147 still exposes a raw hash-only COMPLETE API to trusted leaders, although SHEET 155 finality never accepts leader-provided journal fixtures in place of independently fetched live signed journals. The external rollback signer remains singular and must be secured independently for real deployment. All signatures in the tests use ephemeral local keys. Sequential slot finality and hash-linked durable files do **not** by themselves establish global consensus, atomic commit across unrelated hosts, or malicious-majority resistance. The intermittent historical SHEET 142 concurrency test remains an open inherited risk even after successful runs.