# AETHER-296-RS — AWS Caller Identity and Object Lock Configuration

AETHER-296 adds a read-only AWS SigV4 **GetCallerIdentity** request to regional STS and two read-only S3 bucket metadata requests: **GetBucketVersioning** and **GetObjectLockConfiguration**. The client uses the existing bounded public-IP DNS and TLS hostname-pinned AETHER-264 transport. It accepts only AWS service hosts, restricts methods to GET, rejects redirects, non-200 statuses, duplicate response headers and oversized responses, and retains exact response XML bytes, a request SHA-256 and selected response metadata without storing credentials. Credential access is through AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY and optional AWS_SESSION_TOKEN environment variables; do not commit credentials.

The new correlation gate compares the STS caller-account number to a separately provided explicit account pin; verifies bucket versioning is Enabled; requires the bucket Object Lock configuration to report Enabled; compares the exact object-version pin and retention mode/date between existing AETHER-295 HEAD and GetObjectRetention outputs; and refuses cross-region S3 response hosts.

**Evidence limits:** STS GetCallerIdentity identifies the credentials used for that request, **not the owner of a separately named bucket**. Bucket Object Lock configuration does not by itself prove that a specific version is retained, cannot prove independent custody and is not a provider-issued cryptographic storage receipt. The raw XML and response headers are protected by the TLS session but are not independently signed provider statements. These calls have not been exercised against a real AWS account or storage provider in this phase. The AETHER-295 Ed25519 clock verifier remains available, but independent controller ownership and accurate elapsed time remain unverified. Any request requiring provider credentials must be explicitly authorized. No credentials or token values are written to the journal/report.

The adapter intentionally avoids side-effecting write methods, cross-account assumptions, generic URL redirects, and non-AWS endpoints. Existing phase files/frozen histories are unchanged.

## Offline regression

    python3 -m unittest discover -s aether/296 -p 'test_*.py' -v

## Opt-in AWS read-only capture

    AWS_ACCESS_KEY_ID=... AWS_SECRET_ACCESS_KEY=... python3 aether/296/account_lock_audit.py aws --kind IDENTITY --region us-east-1
    AWS_ACCESS_KEY_ID=... AWS_SECRET_ACCESS_KEY=... python3 aether/296/account_lock_audit.py aws --kind VERSIONING --region us-east-1 --bucket your-bucket
    AWS_ACCESS_KEY_ID=... AWS_SECRET_ACCESS_KEY=... python3 aether/296/account_lock_audit.py aws --kind LOCK_CONFIGURATION --region us-east-1 --bucket your-bucket

For offline correlation, supply a JSON bundle containing identity, versioning, lock, head and retention reports along with explicit --expected-account and --expected-version. These are consistent-input checks, not an authorization grant.

    python3 aether/296/account_lock_audit.py correlate --bundle verified-readback-bundle.json --expected-account 123456789012 --expected-version EXPLICIT_VERSION_ID

Operational authority HOLD; physical qualification 0%. Independent external clock custody and immutable object retention remain UNVERIFIED.

Next natural bound AETHER-297-RS: bind bucket owner with explicit ExpectedBucketOwner on S3 requests, compare GetObjectRetention/HeadObject against account-scoped policy evidence, and persist an immutable, credential-redacted transcript. Do not mistake self-pinned identities or mirrored corpora for three independent witnesses.
