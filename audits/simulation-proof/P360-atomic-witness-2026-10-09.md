# P3.60 — Atomic local witness reservation
Date: 2026-10-09.

P3.59 vote format is preserved. Exclusive local-file creation reserves (witness, context, epoch) before signing; a winner persists the signed record and subsequent identical submissions return its signature. Conflicting submissions fail closed. Incomplete reservations are never automatically re-signed. Node v22.16.0 local stress: PASS 6 assertions, 64 concurrent attempts, one unique first signature, 32 conflicting requests rejected, restart duplicate recovery and next-epoch issuance. Other colliding attempts may return pending-recovery rather than duplicate while write is in progress.

Security boundaries: this is local filesystem coordination, not durable consensus across remote machines; do not assume NFS semantics, power-loss guarantees, compromised keys, or two processes using different directories. A production implementation must verify directory fsync guarantees, key custody, crash injection and recovery procedures. No relation to physical photon hypotheses is claimed.
