# OASIS final two-device acceptance — release-candidate field guide

**Current status: software gates 1–5 PASS; gate 6 requires a real two-device run.**
This release adds mutual TLS 1.3 encryption + two-way certificate authentication over the existing signed OBF2 + durable journal, without changing any frozen math, token mappings, or wire encoding. It is not Internet-hardened multi-tenant software: it uses one trusted sender and one journal writer per receiver, and should only be exposed on a private LAN/VPN with firewall restrictions.

## On the machine preparing keys (requires OpenSSL, Node.js 22+)

From the extracted ZIP root:

```bash
node architecture/diatom-diamond/final-six/setup-keys.mjs ./oasis-keys
```

Three folders are created. Move `oasis-keys/server` *only* to receiving computer B; `oasis-keys/client` *only* to sending computer A. Store `oasis-keys/root-private` securely offline; **never copy the private CA key to either endpoint**. Don't store these keys in GitHub or cloud storage. On Unix, restrict file permissions; on Windows, restrict NTFS ACLs. Rotate test certificates before expiration (90 days).

## Receiving computer B

On a private trusted LAN or VPN, find B's *local* address (e.g. `192.168.1.20`); allow TCP port 32443 from computer A only. In the extracted ZIP root, with the `server` certificate folder available:

```bash
node architecture/diatom-diamond/final-six/remote-mtls.mjs serve 192.168.1.20 32443 ./receipts/commits.jsonl ./server/server.key ./server/server.crt ./server/ca.crt ./server/sender.pub.pem OASIS_TEST
```

The receiver prints `READY OASIS mTLS`. Journal must be stored on a durable local disk. Keep a backup of the journal and access-control configuration.

## Sending computer A

Copy only the `client` credential folder to A. Connect to B's actual LAN address:

```bash
node architecture/diatom-diamond/final-six/remote-mtls.mjs send 192.168.1.20 32443 ./client/ca.crt ./client/client.crt ./client/client.key ./client/sender.private.pem OASIS_TEST final-event-001
```

Expected authenticated ACK: `"status": "APPLIED"`. Repeat **the exact same command** with `final-event-001`: expected authenticated ACK `"status": "DUPLICATE"`, same receipt hash. That demonstrates a durable, deduplicated receipt for a retry.

For the loss/restart gate, temporarily disconnect the network or stop B *after* its first successful commit, restart B, and resend the **same event ID**. It must yield `DUPLICATE`; receipt count must remain one. For controlled crash timing, the receiver supports `--test-crash final-event-002` at the end of its startup command: this exits immediately after journal fsync before ACK, then the sender's first call should fail, B is restarted without the crash flag and A retries `final-event-002` to obtain `DUPLICATE`. **Use only on disposable test journals.**

## Accept Gate 6 only when observed

- Two separate physical computers are confirmed, with different OS and hardware/network addresses.
- Server certificate and client certificate are verified under the private CA, with TLS 1.3; wrong CA or absent client certificate is rejected.
- Signed 444-byte ASTROPHAGE/OBF2 payload is accepted and acknowledged; wrong Ed25519 signature rejected.
- A disconnect/restart followed by replay of the same sender/event ID gives `DUPLICATE`, not a second durable receipt.
- No frozen code modifications; record date, device identifiers (no secrets), receipt hash and result.

Until this has happened, final production acceptance **remains 5/6 / HOLD**. Successful localhost tests establish the software behavior only.

## Security notes

- TLS authenticates and encrypts the channel; the separate Ed25519 signature authenticates the message origin. Neither proves the *facts* inside the message.
- CRC32 and OBF2 rails protect against accidental corruption, not hostile forgery.
- Journal hash chaining detects unsophisticated after-the-fact edits but is not a tamper-proof external ledger. No fully durable distributed consensus or exactly-once external side effects are promised.
- This proof-of-deployment is **not** a license to expose an unreviewed single-writer service to the public Internet; restrict the firewall to LAN/VPN.