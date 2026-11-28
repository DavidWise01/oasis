# AETHER-295-RS — Read-Only SigV4 Metadata and Pinned Clock Signatures

This phase adds a restricted **AWS S3 read-only SigV4 adapter** plus a separate Ed25519 clock-claim verifier. The adapter signs only HEAD and GET metadata requests (no PUT/POST/DELETE), requires an explicit nonempty object version, validates the exact S3 region service host, applies public DNS/IP checks and TLS hostname verification through the AETHER-264 pinned-address transport, rejects redirects, oversized/encoded responses and missing metadata, and records the request hash and original raw response bytes **without** writing AWS secret material into output. The optional session token is included in SigV4 signing.

The HEAD request checks the x-amz-version-id header against the explicit version pin. The GET retention request parses the S3 Retention XML mode and until-date. Transport is a signed CLIENT request over TLS, not provider-signed object storage evidence, and version metadata alone cannot prove independent external custody or a fully authenticated AWS account identity. This initial adapter is intentionally narrow: only the regional endpoint s3.REGION.amazonaws.com and objects identified as path bucket/key; no redirects, arbitrary origins, writable methods or IAM actions. It does not yet bind the returned object metadata to an independently observed AWS account ID or official Object Lock configuration. When used with real credentials, the access key must have only the minimal HEAD/GetObjectRetention permissions; credentials are read from AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, and optional AWS_SESSION_TOKEN environment variables and must never be committed.

The separate clock verifier checks two Ed25519 signatures against the supplied public key's separately pinned SHA-256, each claim's historical window head, nonce uniqueness, preceding signature-chain digest and strictly increasing claimed epoch millisecond timestamps. This establishes signature and content parity, **not independent clock authority or accurate elapsed time**. No clock or S3 provider is contacted by offline tests.

Run:
    python3 -m pip install 'cryptography>=43,<47'
    python3 -m unittest discover -s aether/295 -p 'test_*.py' -v

Opt-in AWS read-only metadata:
    AWS_ACCESS_KEY_ID=... AWS_SECRET_ACCESS_KEY=... python3 aether/295/authenticated_provider.py aws --host s3.us-east-1.amazonaws.com --region us-east-1 --key bucket/object-key --version EXPLICIT_VERSION_ID --kind HEAD

Read-only retention:
    python3 aether/295/authenticated_provider.py aws --host s3.us-east-1.amazonaws.com --region us-east-1 --key bucket/object-key --version EXPLICIT_VERSION_ID --kind RETENTION

Clock qualification:
    python3 aether/295/authenticated_provider.py clock --claims signed-clock.json --clock-pem pinned-clock.pem --pinned-key-sha256 SHA256_OF_PEM_BYTES --heads window-head-digests.json

Every path remains operational HOLD, physical qualification 0%, source ancestry unverified. Earlier AETHER freezes and modules remain unchanged.

Next natural bound — AETHER-296-RS: test real scoped read-only credentials against provider account identity and object-lock metadata, bind canonical HTTP response header bytes and version identifiers, and require external clock identity anchored independently from the operator-controlled trust source.
