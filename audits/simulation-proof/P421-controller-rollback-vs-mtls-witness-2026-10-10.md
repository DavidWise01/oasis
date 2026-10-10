# ROOT0 P4.21 — controller rollback against retained mTLS witness

2026-10-10, Node v22.16.0 + locally generated test CA/OpenSSL.

**Verified locally:** `node test_p421.mjs` PASS with **13 assertions**, repeat elapsed **565.763 ms** (including certificate generation, process startup and SIGKILL recovery).

## Tested path
1. TLS 1.3 mutual certificate and Ed25519 request-authenticated witness launched as separate child process.
2. Controller and witness each retain independent SQLite epoch/head data; initialized at epoch 0 and advanced to epoch 3.
3. Controller-only database restored to prior coherent epoch-0 snapshot while newer witness remained untouched. Reconciliation rejected with `controller-rollback`.
4. Witness SIGKILL/outage denied new reads; restarting same retained witness recovered epoch 3 and continued to reject old local history.
5. Direct attempt to publish old epoch refused; administrator's signed RECOVERY_REVIEW acknowledged without mutation.

## Scope limit
**Same host only; no actual second host or administrative trust boundary.** Both witness and controller stores and signing keys are in one temporary directory. Host-level coordinated rollback remains possible, and this test does not establish monotonic storage in an independent security domain. Service does not permit safe automated repair of local-ahead history; recovery is manual. Experiment uses simulated logical epochs, not physical clock metrology.

Source `p421_controller.mjs` committed; exact 13-assertion integration runner, dependencies, README and JSON shipped as conversation `p421_bundle.zip`. ZIP SHA-256: `76ca0958bb1994eb7eb772dafa6ed643280ab5e60654da4932e97e2877096505`.

Next P4.22: run the service on a truly independently administered host/key domain and test attacker-controllable local snapshots against an independently retained witness.