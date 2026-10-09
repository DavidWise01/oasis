# SHEET 156 — Quorum-Replicated Rollback Floor / Signed Witness Admission

**Status:** consult `new-test-report.json`, `combined-exit.txt`, `combined-run.log` and `browser-test.log` for exact reproducible test status. This is a *local experimental implementation*, not an independently deployed distributed database.

## Upgrade

SHEET 155 used a single externally signed rollback-floor service. SHEET 156 replaces **that authorization decision** with three mTLS-isolated witness processes, each owning an Ed25519 key and separately persisted append-only hash chain. The old S155 signed floor envelope is retained for compatibility, but **finality replicas and the anchor gateway also require two fresh, matching `S156:HEAD` signatures over a caller-supplied random nonce**. A compromised proxy key by itself cannot admit a stale or forged floor.

A new floor row requires **two different signed FINAL approvals**, then **two signed witness PREPARE votes persisted before they are issued**, then **two witness COMMIT replies**. The floor proxy re-reads a live two-witness majority before returning success. One witness can be lost without stopping reads; two losses make reads and slot admission fail closed. Witnesses reject conflicting prepares even if the presenting client controls two valid FINAL signer keys. That conflict survives restart because the pending row is durable.

## Executable source

- `witness-verify156.js`: canonical row derivation, FINAL/PREPARE certificate validation, independently verified live head proofs.
- `witness156.js`: separate-key mTLS durable per-witness protocol, `/read`, `/prepare`, `/commit`, conservative conflict handling.
- `floor-quorum156.js`: S155-compatible facade, majority vote collector, fresh nonce-bound majority reads.
- `finality-replica156.js`: SHEET155 finality code with *required native witness majority proof* in `floorRead()`.
- `anchor-gateway156.js`: SHEET155 admission gateway with *required native witness majority proof* before anchor advancement.
- `gate156.js`: actual subprocess/TLS adversarial tests with three witness keys, three finality keys, three live authority replicas, segmented physical writer, checkpoint signer and gateway.
- `baseline155/`: byte-for-byte frozen previous release including the entire older tree.
- `KERNEL-ASCII.txt`: complete 56-stage end-to-end execution pipeline and failure matrix.
- `index.html`: standalone SVG fault viewer; `browser-check.py`: Chromium interaction test.

## Run

```bash
node gate156.js
bash run-all.sh
python browser-check.py
```

Node.js 22+, OpenSSL, Bash, and optionally Chromium + Playwright are required.

## Explicit boundaries

Every TLS service runs in separate local Node.js processes but **on one physical host**. The witness keys are ephemeral test keys and not independently administered. A majority-signature floor protects against a single proxy/key fault, not a compromised witness majority; it is *not a formal proof of global linearizability or cross-host atomic commit*. Reconciliation for a lagging minority witness after an interrupted commit is not automated. A witness that has signed one conflicting pending row refuses to sign a different row at that slot, favoring safety over availability. The trusted S147 raw COMPLETE endpoint and historical S142 timing-sensitive assertion are inherited and remain unresolved.