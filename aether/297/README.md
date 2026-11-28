# AETHER-297-RS — Expected Bucket Owner and Credential-Redacted Evidence Ledger

This phase adds a read-only S3 SigV4 capture gate with explicit x-amz-expected-bucket-owner binding. The owner must be a 12-digit ASCII AWS account ID and is included in **SignedHeaders** and the HMAC signature; S3 rejects a mismatched expected owner with HTTP 403. AWS API reference: GetObjectLockConfiguration, GetObjectRetention and HeadObject.

The adapter permits exactly four operations against a single regional S3 endpoint, bucket, object key and version:
1. GET BucketVersioning (requires Enabled);
2. GET ObjectLockConfiguration (requires Enabled);
3. HEAD Object using explicit versionId (requires exact returned x-amz-version-id and object-version retention metadata);
4. GET ObjectRetention using the same versionId (requires mode/date equality with HEAD).

The object key and request path are represented by SHA-256 in durable evidence to avoid leaking sensitive URL paths. The transcript stores exact response body bytes as base64, response SHA-256, a strictly selected allowlist of noncredential response headers, operation, signed request SHA-256 and the expected owner pin. It **never** stores SigV4 Authorization, access key, secret, session token or cookies.

For each accepted capture, all four response records are written as a single canonical manifest into SQLite WAL using BEGIN IMMEDIATE, synchronous=FULL and an append-only SHA-256-linked history. Challenge nonces cannot be reused, and recovery recomputes record digests, observed header hygiene, historical head linkage, and an optional externally supplied historical prefix pin. This is not externally immutable storage: a party controlling the complete DB and its prefix pin can still roll both back.

## Evidence boundary

Successful S3 responses with an expected owner guard make account-number substitution harder at the S3 request boundary. This is **not** independent physical custody, independent provider-signed receipt validation, proof of retained data's content, or proof of independently held trust roots. Bucket configuration also does not itself prove a given version has retention; that is why HEAD and GetObjectRetention are compared. Local clock/CI time is not independent authenticated elapsed-time evidence. The source corpus (GitHub and its mirrored Pages/0root.ai presentation) is one ancestry, not several independent witnesses.

GitHub tests use a mocked HTTPS transport and do not send real AWS requests. Live capture is opt-in only and requires read-only AWS credentials made available as environment variables. Restrict IAM to the specific bucket and object version; do not commit credentials.

Offline tests:
    python3 -m unittest discover -s aether/297 -p 'test_*.py' -v

Live opt-in:
    AWS_ACCESS_KEY_ID=... AWS_SECRET_ACCESS_KEY=... AWS_SESSION_TOKEN=... python3 aether/297/owner_bound_ledger.py capture --db /tmp/aether297.sqlite --region us-east-1 --bucket witness-vault --key archive/payload.json --version EXPLICIT_VERSION --expected-owner 123456789012 --nonce unique-capture-nonce-297

Read-only forensic audit:
    python3 aether/297/owner_bound_ledger.py audit --db /tmp/aether297.sqlite --prefix-seq 1 --prefix-sha256 <64hex>

Caution: provider-native operations and IAM permission names should be independently reviewed before production use. Physical qualification stays 0%, operational authority HOLD.

## Next natural bound — AETHER-298-RS

Externally preserved and independently authenticated provider version evidence; review SigV4 canonical-request conformity against an official SDK, test full crash/restart history and remote snapshot custody, and perform a permission-scoped provider sandbox trial. Do not grant ACT on signature agreement alone.
