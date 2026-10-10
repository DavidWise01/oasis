# ROOT0 P4.25 — Live nonce challenge-response benchmark (2026-10-10)

Local Node.js v22.16.0 run: **13/13 assertions PASS**, final run about 26ms. A loopback TCP witness signs deployment, fresh 192-bit challenge nonce, epoch and head with Ed25519. Verifier checks pinned signing key, issued nonce, 100ms test expiry, and in-memory highest accepted epoch/head. Tested valid challenge, replay, unauthorized signer, expiry, changed digest, old epoch, same-epoch fork, next epoch, substituted nonce, unsolicited response, 20 concurrent older-epoch responses, live network response, and outage.

A public KeyObject normalization bug was caught on first run and repaired before passing rerun.

**Critical scope:** proof of signed challenge response/key possession on localhost only. The server uses raw TCP in this test—not TLS or mTLS. The P4.20 transport exists separately but was not integrated or tested here. Verifier floor and issued challenges are in memory; restart loses them. No second host, independent key custody, real external certification, or durable nonrollbackable witness. Actual ROOT0 host certification remains NOT CERTIFIED. ZIP SHA-256: `08913978d9d41dc467505ab1880e247d63eef8ec040432a74a34204ff1354ae0`.

Runnable exact local source, regression test, README and measured results in P4.25 conversation ZIP. Next P4.26 integrate challenge binding into mutually authenticated TLS and persist challenge/floor state on the independent witness.