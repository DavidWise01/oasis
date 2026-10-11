# SHEET 237 — Independent mTLS Authority Process Crash & Recovery

Executed: 31/31 S237 integration assertions; 15/15 S235 broker boundary regression; 16/16 S236 store-failure regression. Total 62/62 assertions across three separately executed gates.

S237 launches mTLS target and floor as independently killed and restarted Linux processes, plus a separate UID-isolated Unix broker. After target commit and floor persisted ACK, SIGKILL then process restart preserves target signed receipt and exact floor signed ACK returned over /status. The broker is also killed and restarted after signed reconciliation; its binding and floor generation persist, and repair replay fails. Negative tests include missing TLS client certificates, forged signatures, rejected Unix peer identity and stale recovery.

Exact tested ZIP: SHEET237-independent-service-restart.zip, 28,060 bytes, 17 files; SHA-256 e645e55c68660d52f7a98927cce6b728bdac9a9a26a683a3b5c4d8e6036bc1aa. Includes gate237.py and gate235.py/gate236.py regressions plus dependencies.

Limits: Integrated WAL is created as a valid fixture rather than exercised through full original protected writer. Four-store writer crash has a separate simplified fixture. This does NOT validate simultaneous full-service faults, network partitions, physical power loss, or cross-store atomicity. Milestone progress remains 90% (9/10 locally demonstrated), not production readiness.

Next S238: original protected WAL writer plus independent mTLS processes, SIGKILL and ACK-loss relay during broker commit.