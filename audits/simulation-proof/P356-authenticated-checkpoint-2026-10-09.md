# P3.56 — Authenticated checkpoint stress

2026-10-09. Ed25519 signatures authenticate checkpoint context, epoch, length, and SHA-256 chain head. Tests used ephemeral generated keys, not committed secrets. Verifier rejects replay via externally retained epoch/length, unauthorized signer, forged stamp, suffix truncation, changed context and an alternative full-length history signed by the same key at a higher epoch if it does not descend from the independently retained accepted head. This is chain continuity, not global fork consensus.

Local Node v22.16.0: PASS 30 assertions over three envelopes, 1440 records each. Persistence of the trusted checkpoint and secrecy of signing keys are application responsibilities. A new verifier lacking trusted state cannot detect a self-consistent alternative signed history. Remote CI not verified.
