# Phase 2 / P2.1 — Real consensus integration boundary

**Decision:** Stop adding simulated leader-election code and bind `IT3/v1` to a vetted **external linearizable, replicated key-value store**. This module defines a fail-closed adapter interface; it is not a Raft implementation or a deployment.

The backend's `submit(key,value)` must return only once the server reports a quorum-committed revision and exact committed bytes. `read(key)` must be a linearizable, not serializable/stale, read. `publish` verifies exact byte equality, confirmed positive revision, read revision ordering, and re-decoded timestamp. It returns a receipt only then.

## Next integration target
- Deploy a three-member etcd cluster with TLS 1.3 peer/client authentication, unique credentials, separate data volumes, stable member identities and secure rotation.
- Implement a concrete etcd v3 client/backend with explicit response-header revisions and linearizable Range; do **not** treat this mock as a deployment.
- Use immutable create-only keys or transaction compare-and-put to avoid an existing record being overwritten. Define idempotent request IDs and uncertainty/retry policy; plain put can overwrite.
- Record release evidence for process restart, majority loss, quorum read/write, snapshot restore, and backup under real fault injection.
- Retain Step 20's production release gate in BLOCKED state until certified external evidence exists.

Run `cd docs/y2038 && python3 check_phase2_adapter.py` (12 boundary fixtures). The mock validates the adapter **contract**, not actual quorum replication or durability.
