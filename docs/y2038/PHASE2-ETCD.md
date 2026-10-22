# Phase 2.2 — etcd v3 JSON gateway backend

Implements Phase 2.1's `Backend.submit/read` via etcd /v3/kv/txn (CREATE revision = 0 compare, then Put) and /v3/kv/range with `serializable=false` (linearizable read). The top-level response header revision is checked. Requires HTTPS and an SSL context with CA and client certificate/private key. The example uses etcd's **JSON gRPC gateway**, not direct gRPC. Authentication by TLS Common Name may differ in the gateway: configure certificate verification and application-layer authorization appropriately.

Run `cd docs/y2038 && python3 check_phase2_etcd.py`. The seven unit-test methods use an isolated mock transport and do **not** prove a live three-member etcd cluster.

Usage: `backend=EtcdGateway("https://host:2379","ca.pem","client.pem","client-key.pem"); receipt=publish(backend,"rollover-2038",2147483648)`. Never commit credentials.

Outstanding: real certificate provisioning, real 3-node cluster, unique immutable IDs, TLS identity/authz checks, power-cycle testing, quorum loss, independent verification, monitoring and external release attestations. The create-only behavior returns conflict on an existing key, including same-value retries; implement explicit idempotent retry semantics before deployment. Release remains BLOCKED.
