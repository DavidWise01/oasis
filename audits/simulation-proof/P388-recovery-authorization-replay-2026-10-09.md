# P3.88 — Recovery authorization replay and concurrency (2026-10-09)

Executed on Node.js v22.16.0 using P3.87 dependency chain. Result: PASS_WITH_AUTHORITY_ROLLBACK_VULNERABILITY, 12 assertions. A one-time operator Ed25519 authorization is scoped to the witness directory, unique lock ID and nonce. A separately provisioned authorization journal stores consumed grants using exclusive open ('wx'), file fsync and directory fsync **before** removing a lock.

Fault testing: absent offline confirmation rejected; invalid signatures rejected; cross-lock reuse rejected; 64 parallel clearance attempts for one authorization yielded exactly 1 success and 63 rejections; restart with retained authorization journal preserved replay rejection; rebuilt lock with old identity and old authorization rejected. **Critical reproduced flaw:** deleting the authorization journal resets this security state, permitting replay of the old valid authorization against a recreated lock.

Offline quiescence remains a caller assertion, not independently verified. The 'independent' authority is a separate local directory, not a truly nonrollbackable service. No claim of production security, process-fencing, hardware persistence, or consensus. The existing ROOT0 symbolic -+5 + 1 / OSI seven-band 100-layer structure is unchanged.

Runnable artifact: P3.88 bundle delivered in this conversation; source and tests not yet pushed to GitHub. Next P3.89: external fencing epochs, anti-rollback authorization history, and safe lock takeovers under killed-and-restarted workers.
