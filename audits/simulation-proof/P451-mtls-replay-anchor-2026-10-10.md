# ROOT0 P4.51 — TLS protected anchor and durable replay
Date: 2026-10-10.

Local Node v22.16.0 test **14/14 PASS**, last elapsed **484.961ms**, including openssl generation of one-day test CA and both certs. TLSv1.3 minimum, server CA verification and required client certificate, pinned Ed25519 request/response signatures. Separate SQLite replay ledger rejects reused request nonces after real SIGKILL and restart. Signed primary checkpoints epochs 0-2 observed; rollback, fork, forged Ed25519 client identity, missing client TLS certificate, untrusted CA denied. Previously encountered intermittent ECONNRESET caused by unhandled TLS socket error; added socket error handler and changed client close handling, then passing reruns.

**Important limits:** server binds to 127.0.0.1 and both processes share host and administrator. No separate-host test or independently protected storage. Replay nonce store and anchor store are two SQLite transactions; partial failure can record nonce without checkpoint. Ledger has no capacity or pruning. Test CA is not production PKI; TLS peer certificate validation is based on test CA, not mapped to an authorized client certificate fingerprint. No remote service exposure should occur. GitHub service and client implementations committed; regression test remains in ZIP. 

SHA256 P451 ZIP `bf8027877dd6266961bcef72ac387e4376c882e128c5ca8e30e5918213c610d2`.

Next P4.52: atomic anchor+nonce journal in a single DB, bound TLS peer identity, cross-host private network test.