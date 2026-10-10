# P4.17 — durable nonce and witness restart (2026-10-10)

Node.js v22.16.0 local execution, final verified run: **15/15 assertions PASS**, **143.31 ms** end-to-end. Regression starts a separate signed witness process, signs and registers epoch zero, attempts 20 conflicting epoch-one writes (exactly one wins), issues SIGKILL, and restarts witness **without manually deleting the stale socket**. Signed request nonce remains rejected across two restarts in SQLite `seen_nonces` table. Wrong client identity rejected; manual recovery-review requests cannot mutate witness.

GitHub aligned dependencies: `p415_witness.mjs`, `p416_client.mjs` and new `p417_service.mjs`, all in `docs/reality-tensor/dyson-inversions/`. Complete runnable regression and JSON are in the chat ZIP. The 200 layer/200ms and 1e-36 second logical timestamp model is unchanged.

Limits: service and database still share a host, and coordinated rollback of its history remains unprotected. Signed nonce reserve and witness update are separate local transactions (fail closed but potential denial-of-service if crash between them). Socket recovery rejects active listeners based on a connection probe but does not harden all symlink/ownership races or hostile local users. Not a hardware clock test or independently operated witness.

Next P4.18: external-host attested witness, signed recovery request protocol, and coordinated rollback verification.