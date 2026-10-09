# SHEET 147 — Replicated Transaction Authority / Leader Epochs

**Status:** `0e / PASS`, **51/51 new checks**, with **1,017 inherited SHEET 146 lineage checks passing in the latest inherited run**. The SHEET 142 inherited concurrency test has failed intermittently in previous runs; a passing single rerun does not establish its long-run stability.

SHEET 147 preserves the complete SHEET 146 baseline under `baseline146/` without source modification, and introduces an *additive* replicated authority designed to eliminate the single primary authority as an availability dependency in this synthetic test.

## What is implemented

- `replica147.js` — three **separate Node.js processes** with independently persisted election/prepare/commit journals, mTLS caller identity pins, Ed25519-signed votes, monotonic terms, and signed external rollback-floor checks.
- `coordinator147.js` — elect leader (2/3), submit grant/completion/cutover proposals, collect two independently signed prepare votes, certify after two durable commit acknowledgements, recover pending prepared operations, and replay quorum-certified history to a lagging replica.
- `gate147.js` — 51 real-process tests: two candidates competing in the same term, client-certificate and server-pin rejection, leader handoff, node outage, replica resynchronization, an interrupted prepare, transaction grant blocking cutover, conflicting proposal rejection, rollback detection, and duplicate/forged votes.
- `baseline146/` — full inherited production of SHEET 146 (unchanged) including its historical lineage and independent TLS resource tests.
- `index.html` — static, interactive SVG **scenario explorer** with JSON export. Not a live network control surface.

## Run

Requires **Node.js 22+**, `openssl` CLI, `bash`, and ordinary localhost sockets.

```bash
cd sheet147
node gate147.js
bash run-all.sh
```

`run-all.sh` makes an isolated temporary copy of the entire inherited baseline before running its tests, so inherited test fixtures and outputs in the release tree remain unchanged. New test credentials are ephemeral and are stored only in a temporary directory, removed at test completion.

## Commit semantics and fail-closed rules

A proposal is not certified just because the leader received an RPC success. The coordinator first collects **2 distinct verified signatures** on the exact proposed operation and index; it then requires **2 durable commit acknowledgements** matching the expected new log hash. Failures between prepare and commit remain unresolved until the same signed proposal is recovered; they are **never silently abandoned**. A pending transaction grant blocks CUTOVER until a matching completion is certified.

The per-replica journal is hash-linked and revalidated on every request. A separately signed sequence/hash floor demonstrates rollback detection when the floor is held outside that node's state directory. The test fixture stores it in another **local** directory, not an independent transparency service.

## Safety boundaries and limitations

1. **Not a production consensus protocol:** no claims of a complete Raft implementation or Byzantine fault tolerance. State transfer and election concurrency are tested only for the scenarios in `gate147.js`.
2. **Same physical host:** real HTTPS sockets and separate processes are tested, but no independent machine, datacenter, operator, or HSM was used.
3. **Potential liveness loss by design:** a minority unresolved preparation or missing receipt can block a fresh election. Safety is preferred to automatic force-unlock.
4. **No resource integration yet:** the preserved `baseline146/authority146.js` and `resource146.js` are not switched over to the SHEET 147 quorum API. The new authority is independently executable; the last-mile resource adapter is a SHEET 148 task.
5. **No external publication:** cryptographic floor signatures are not a remote third-party anchoring service; rollback beyond an attacker's access to the pins is not established.
6. **No unconstrained global linearizability proof:** the tests do not prove that two independently operated hosts cannot both commit under arbitrary network schedules.
7. **Inherited flake:** SHEET 142 contains a timing-sensitive assertion in a prior frozen test; it is not rewritten or claimed fixed by this release.
8. **Historical SHEET 103 parity** remains outside the verified scope.

## Proposed SHEET 148

Bridge `resource146.js` to the new quorum certificate API. Make protected writes verify a live replicated membership head and retain a certified pending transaction through crash/restart. Test leader disappearance during resource commit and fence old leaders across independently running resources.