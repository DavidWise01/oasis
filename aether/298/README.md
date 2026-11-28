# AETHER-298-RS — SigV4 Reference Parity & Durable Evidence Export

AETHER-298 provides a **read-only, offline qualification layer** over the existing AETHER-297 owner-bound evidence journal. Its SigV4 oracle independently computes canonical request hashes and HMAC signatures with the official AWS botocore SigV4Auth implementation, comparing caller-provided request/vector preimages and signatures. The fixture uses fixed synthetic keys and explicit x-amz-expected-bucket-owner; no real AWS credentials are used or transmitted. **Scope:** the offline reference vector checks parity of the candidate canonical request/signature, not the execution of live AETHER-297 HTTP requests, account ownership, provider-signed evidence, or external custody.

The qualification auditor reconstructs the AETHER-297 SQLite journal read-only. It rejects missing history, gaps, replaced heads, edited canonical manifests, modified raw response bytes, duplicate operation kinds, non-read-only methods, unsafe transcript headers, or mismatched externally supplied historical prefix pins. It validates four operations per manifest: VERSIONING, LOCK_CONFIGURATION, HEAD, RETENTION.

The new freeze-export operation is create-only (O_EXCL, no overwrite), writes canonical JSON with all original retained journal preimages, fsyncs the file and parent directory, reads back the exact bytes, and reports a SHA-256 digest. The export preserves physical_act_allowed=false and custody_attested=false. Failure after successful file creation does not silently destroy or overwrite that evidence; investigate any unverified file left behind. Local disk snapshots and caller-provided prefix pins are NOT externally immutable, and an attacker controlling both may roll both back.

## Local qualification — verified at authoring time

    python3 -m pip install 'botocore>=1.35,<2'
    python3 -m unittest discover -s aether/298 -p 'test_*.py' -v

**21/21 offline regression cases passed locally** in the authoring environment, including a botocore canonical-request/signature parity case, nonce/checkpoint corruption, response redaction, O_EXCL no-overwrite, file readback, and altered snapshot detection. GitHub Actions CI must be checked separately; offline tests are not proof of a live, scoped AWS account/sandbox execution.

## Operator workflow (never run automatically)

    python3 aether/298/qualification.py sigv4 --case synthetic-case.json
    python3 aether/298/qualification.py freeze --db /tmp/aether297.sqlite --out /tmp/aether298-export.json --prefix-seq 1 --prefix-sha256 <sha256>
    python3 aether/298/qualification.py audit --export /tmp/aether298-export.json --db /tmp/aether297.sqlite

Do NOT provide actual AWS secret keys in synthetic-case.json: CLI case files are not credential stores. Only fixed dummy test credentials should ever be used in that mode. All prior phases remain unchanged. Authority HOLD; physical qualification 0%; independent external custody NOT VERIFIED.

## Next natural bound — AETHER-299-RS

Reconcile real AETHER-297 SigV4 canonical preimages against botocore on an authorized, permission-scoped dry-run, perform crash-injection qualification of journal export and recoverable incomplete writes, and add an independent, externally administered high-water archive without allowing a single mirrored ancestry to masquerade as independent custody.
