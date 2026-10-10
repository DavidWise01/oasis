from pathlib import Path
import json, statistics, datetime
B=Path(__file__).resolve().parent
j=json.loads((B/'benchmark164.json').read_text())
lines=['# SHEET 164 — Factorial Benchmark Report','','**Status:** 68/68 new checks PASS; inherited SHEET 163 gate 45/45 PASS in isolated snapshot, exit 0.','', '## Protocol and experiment design','', '- Three independent factors: prefetch window `{1,4}` × durable record batch `{4,8}` × pinned mTLS reuse `{off,on}` = **8 conditions**.','- Two reproducibly shuffled blocks, seed `0x164bad5`; each condition recovers the same 128-record suffix from a 384-record source.','- Signed quorum proof pages, authenticated SHA-256 Merkle extensions, and exactly ordered segment/head fsyncs remain active in every condition.','- Synthetic page completion jitter is deterministic, 3–14 ms according to offset and block; no simulated multi-host network or remote storage.','- Each condition begins with a fresh 256-record target copied from one verified seed. Timing includes recovery handshakes and RPCs but excludes the setup/seed copy.','- The mTLS-off branch creates new authenticated TLS connections per request and **keeps certificate pinning enabled**.','', '## Observed throughput', '', '| Prefetch | Batch | Reuse TLS | Block 1 rec/s | Block 2 rec/s | Mean/median rec/s | TLS connections/request |','|---:|---:|:---:|---:|---:|---:|:---|']
for s in sorted(j['policySelection']['scored'],key=lambda x:(int(x['key'].split('/')[0]),int(x['key'].split('/')[1]),x['key'].split('/')[2])):
    w,b,t=s['key'].split('/'); rs=[r for r in j['results'] if (r['window'],r['batch'],str(r['reuseTls']).lower())==(int(w),int(b),t)];rs=sorted(rs,key=lambda x:x['block']); pairs=', '.join(f"{r['tlsConnections']}/{r['requests']}" for r in rs)
    lines.append(f"| {w} | {b} | {'on' if t=='true' else 'off'} | {rs[0]['recordsPerSecond']:.2f} | {rs[1]['recordsPerSecond']:.2f} | **{s['medianRowsPerSecond']:.2f}** | {pairs} |")
e=j['effects']
lines+=['', '## Factor-level marginal means (descriptive, not causal confidence intervals)','', '| Factor | Low condition | High condition | Difference (records/s) |','|---|---:|---:|---:|']
for k,v in e.items():lines.append(f"| {k} | {v['lowMean']:.2f} | {v['highMean']:.2f} | {v['difference']:+.2f} |")
w=j['policySelection']['scored'][0];slow=j['policySelection']['scored'][-1]
lines+=['',f"Highest two-trial median: **{w['key']} → {w['medianRowsPerSecond']:.2f} records/s**. Lowest median: {slow['key']} → {slow['medianRowsPerSecond']:.2f} records/s. Their cross-factor ratio is {w['medianRowsPerSecond']/slow['medianRowsPerSecond']:.2f}×, **not** a controlled estimate of any single optimization.", '', '## Holdout and crash injections','',f"- Chosen policy: `{json.dumps(j['policySelection']['selected'],sort_keys=True)}`.", f"- Independent holdout: **{j['holdout']['rows']} rows**, **{j['holdout']['seconds']:.4f} s**, **{j['holdout']['recordsPerSecond']:.2f} records/s**. Starts at 248 to exercise segment rollover.", '- Actual child-process kill after durable segment/head persistence but before the acknowledgement; restart resumed the original signed transaction and converged to the correct Merkle root without duplicates.', '- The crash test’s reported post-restart duration **excludes the pre-crash period**, so it is not directly comparable to the factorial throughput figures.', '', '## Verification and limits','', '- 68/68 new checks, exit 0. A separate untouched snapshot of SHEET 163 passed 45/45, exit 0.', '- Every measurement is one-host loopback mTLS with synthetic keys and local disk. TLS connections are authenticated even when reuse is disabled.', '- The selected policy was chosen from just two repetitions per configuration: selection bias, caching, and run-order effects remain possible.', '- All 16 factorial runs use the same source history and shared source processes, limiting repeated setup variance but not eliminating host scheduling noise.', '- The proof page is still a bounded 8-record unit; the 4-record factor splits already-verified pages into smaller durable commits.', '- Crash injection covers one chosen policy; it is not a proof of all possible power failures, multi-host partitions, or Byzantine behavior.', '- Cross-host consensus and the unresolved historical SHEET 142 timing-sensitive assertion are not claimed fixed.', '', '## Exact reproducibility','', '```bash','node gate164.js','python make_docs164.py','python browser-check164.py','bash run-inherited163.sh','```','','Raw machine-readable measurements: `benchmark164.json`; command logs: `gate164.log`, `audit/inherited163.log`.']
(B/'BENCHMARK-REPORT.md').write_text('\n'.join(lines)+'\n')
ascii='''OASIS / ROOT0 / SHEET 164 — FACTORIAL PERFORMANCE AND RECOVERY
============================================================
INPUT : signed 2/3 witness head + independently pinned floor
  | 01   Client authenticates 384-record Merkle checkpoint
  | 02   Verify source quorum, resource, hash and final root
  | 03   Load durable target cursor at 256 (holdout: 248)
  | 04   Select candidate from 2 × 2 × 2 policy lattice
  v
 +-------------------- PREFETCH WINDOW --------------------+
 |  WINDOW 1 (serial)             WINDOW 4 (parallel)        |
 |  PAGE0 -> check               PAGE0 -> PAGE1 -> PAGE2 ...|
 |                               |                       |   |
 |                           out-of-order responses possible |
 +-------------------------------+--------------------------+
                                 |
                         ORDERED PAGE BUFFER
                                 |
                     VERIFY Ed25519 + MERKLE EXTENSION
                                 |
               2 FACTORS: BATCH 4 OR BATCH 8
                                 |
                SPLIT AT 256-RECORD SEGMENT BOUNDARY
                                 |
                         EXCLUSIVE WRITER LOCK
                                 |
                        DURABLE SEGMENT FSYNC
                                 |
                         DURABLE HEAD FSYNC
                                 |
                         ADVANCE TRUSTED CURSOR
                                 |
              3RD FACTOR: TLS KEEPALIVE OR FRESH TLS
                  (CERTIFICATE PINNING ON BOTH)
                                 |
            +--------------------+-------------------+
            |                    |                   |
            v                    v                   v
          CONTINUE             CRASH              ERROR
            |                    |                   |
          PAGE+1          SIGNED STATUS           REJECT
            |             RESTART NODE         FAIL CLOSED
            |             REPLAY CURSOR            |
            |             NO DUPLICATES           |
            +--------------------+                   |
                                 |                   |
                            COMPLETE ROOT            |
                                 |                   |
                           VERIFY FINAL HEAD         |
                                 |                   |
                          NEXT VERIFIED STATE     QUARANTINE

EXPERIMENT CONTROL
  |- 8 configurations / 2 randomized blocks = 16 timed runs
  |- each run uses same certified source and fresh 256-row target
  |- deterministic 3–14ms synthetic page-tail jitter
  |- independently measure throughput, TLS connections, requests
  |- choose fastest median of two replicates (bounded policy)
  |- holdout: new target at 248, crosses segment rollover
  `- real child crash after fsync, before ACK, restart + recovery

SECURITY/PROVENANCE
  SHA-256 indexed segment tree -> inclusion -> extension
  resource Ed25519 -> 2/3 witness signatures -> external pin
  only ordered writes may change durable state; speculative reads
  are discarded after any ambiguous cursor step.

UNVERIFIED: cross-host durability, all power-loss windows, old
SHEET142 intermittent assertion, statistical speed guarantee.
'''
(B/'KERNEL-ASCII.txt').write_text(ascii)
readme='''# SHEET 164 — Factorial Merkle Recovery Tuning

**Status:** 68/68 new checks PASS, exit 0. **Inherited SHEET 163:** 45/45 PASS in an isolated copy, exit 0. Full historical nested runner not executed.

This additive build preserves the complete SHEET 163 release under `baseline163/` and introduces a performance-tuning experiment without weakening Merkle or mTLS verification.

## Components

- `transport164.js`: optional TLS connection reuse, pinned certificate verification in both modes.
- `pipeline164.js`: signed quorum recovery with fetch window 1–4, ordered cursor writes and bounded physical segment batches.
- `gate164.js`: randomized 2×2×2 factorial, measured A/B, source-root assertions, TLS connection assertions, segment rollover holdout, real process-kill recovery.
- `benchmark164.json`, `BENCHMARK-REPORT.md`: raw measurements, policy scoring, factor means, caveats.
- `KERNEL-ASCII.txt`: full kernel pipeline, recovery branches, and verification boundaries.
- `index.html`: interactive measured-condition viewer.

## Run

```bash
node gate164.js
python make_docs164.py
python browser-check164.py
bash run-inherited163.sh
```

Tests require Node.js 22, OpenSSL, POSIX fsync/rename, and loopback networking. One physical host only. Full ancestor regressions remain unrerun. See benchmark report for experimental limitations.
'''
(B/'README.md').write_text(readme)
print('created docs',len(lines))
