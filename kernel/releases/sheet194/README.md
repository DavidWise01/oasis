# SHEET 194 — Authority-Bound Target Evidence

**Local execution:** 14/14 focused PASS (`python gate194.py`). Standalone loopback HTTPS mTLS authority validates an Ed25519 target receipt, two distinct repair approvals, matching resource/nonce/input/WAL hash/generation and monotonic SQLite floor before returning signed Ed25519 acknowledgment.

Rejected: missing or forged target receipt, untrusted target signer, one vote, duplicate signer's vote, mismatched approval, absent mTLS client certificate, replayed generation, forked previous hash and tampered signed floor. Authority outage fails closed.

**Executable ZIP:** `SHEET194-authority-evidence-gate.zip`, 6986 bytes, SHA-256 `2c836784bd1e8842a11628e45320340f36dea4fd1c2a5fbf949db333ba32575c`. Includes `authority194.py`, `authority193.py`, `gate194.py` and README. This GitHub commit is release documentation only; executable sources are in the accompanying ZIP.

**Boundaries:** One physical host, local ephemeral PKI/key fixtures. Signed receipts are fixtures rather than independently fetched from a remote target; the S190/191 live repair is not connected. TLS client certificate is trusted via the test CA but not role/resource-scoped. Signature issued after SQLite floor commit; ACK-loss can leave uncertainty. No host partition, full inherited regression or physical power-loss test.

Next SHEET 195: role-scoped client authorization, independent target receipt RPC, and committed-floor lost-ACK reconciliation.
