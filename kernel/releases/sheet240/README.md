# SHEET 240 — Dual-Branch Recovery Alignment

**Executed:** S240 orchestrator 14/14 PASS, S239 mid-prepare test 17/17 PASS, S238 original-WAL mTLS recovery 36/36 PASS. **67/67 assertions across three separately executed gates.** Prepare-only remains quarantined with no invented commit or floor advancement, even with correctly signed but inapplicable evidence. Committed orphan accepts signed target/floor repair exactly once, survives authority/broker restarts and preserves original WAL ancestry.

**Exact tested ZIP:** SHEET240-dual-branch-recovery.zip (74,044 bytes, 51 files), SHA-256 `ec8c35b903c630a26f1721dc2630311175f2aa5c1fd61020c3a7454553870eb9`. Contains original Node S176 source, gate240.py, gate239.py, gate238.py, mTLS authority/broker dependencies and README. Python gate code on GitHub mirrors the tested orchestration. Linux root, Node and cryptography prerequisites.

**Important limitation:** The incomplete prepare and committed-orphan recovery were tested in *separate scenarios*. There was no simultaneous multi-service interruption or remote network partition; power-loss durability and cross-store atomicity unproven.

**Milestone progress: 90% (9/10 local demonstrations)**, not production readiness.

Next SHEET 241: combine simultaneous faults and distinguish prepare-only vs committed orphan in an auditable same-lifecycle scenario.
