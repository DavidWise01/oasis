# P4.10 — Authenticated genesis is not recovery (2026-10-10)

Node.js v22.16.0 local regression: **21/21 assertions PASS**; final rerun 6.21 ms. New `GenesisAuthority` ordinary constructor fails closed if its SQLite store is missing. A separate explicit provision method requires an Ed25519 operator signature bound to deployment and nonce. Provisioning refuses existing stores. Subsequent epoch advancement must be consecutive, and simulated exception before SQL commit rolls back cleanly. Normal restart retains history.

**Reproduced critical limitation:** restoring a coherent old SQLite snapshot passes local validation; its epoch value regresses undetected. Also, if all records are wiped, an operator grant signed previously remains cryptographically valid and could be reused in an explicit fresh provision. A grant is not a separately trusted single-use token. A local file-existence check is not an atomic multiprocess genesis lock, and no actual SIGKILL or hardware power-loss fault was performed.

Canonical `{-{+{%}+}-}` retained. This is a focused security gate integrated at the interface/design level, not end-to-end validation of the 200-layer clock or DIATOM. External nonrollbackable authority and authenticated publish/recovery intent are still required.

GitHub includes executable `p410_genesis.mjs` and `test_p410.mjs`. Reproducible ZIP and JSON output also provided in current conversation.

Next: P4.11 external single-use genesis witness, atomic multiprocess bootstrapping, and killed-process tests.