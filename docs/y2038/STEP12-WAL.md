# Step 12 — persistent WAL and leader-term fencing

Single-node prototype, not full consensus. Run `python3 docs/y2038/step12_wal.py`.

Provides persisted term increase, stale-term rejection, append-only fsynced JSON records carrying IT3 packets, SHA-256 chaining, and restart readback. Local check set: six cases including torn-tail rejection.

## Limitations

No lock against multiple processes writing simultaneously; no inter-node replication, election, quorum, or committed-index protocol. A crash can leave an incomplete log tail, which is rejected rather than automatically recovered. Unkeyed hashes provide integrity checks against accidental tampering but not authentication. Directory sync is included for initial path creation and term replacement, not a guarantee against storage-controller lies or physical power loss. Next step uses an established Raft model and WAL replay policy.

Remaining steps: 13 consensus/elections; 14 quorum replication; 15 partitions; 16 authenticated transport; 17 snapshot/restore; 18 fault injection; 19 formal verification and multi-host validation; 20 production hardening.
