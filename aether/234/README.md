# AETHER-234-RS — Hosted Archive Member Adjudication

Phase XX, next evidence boundary following AETHER-233.

The AETHER-233 API response and returned ZIP container may be hashed, but hashing the ZIP does **not** establish the integrity of individual files, trustworthy manifest ancestry, independent witnesses, original physical captures, or physical ACT authority.

This separate, read-only validator checks a hosted ZIP against a caller-supplied, independently pinned map of exact filenames to SHA-256 digests. It rejects missing/extra/duplicate entries, path traversal, nonregular entries, encrypted entries, malformed containers, size/expansion risks, and member digest mismatch. The report hashes observed member bytes but never includes their contents.

Example (the inputs must be real, not invented):
```bash
python3 aether/234/verify_hosted_zip.py --zip hosted.zip --manifest pinned-members.json --out acquisition-adjudication.json
python3 -m unittest discover -s aether/234 -p 'test_*.py'
```

A matching manifest produces only `MEMBERS_MATCH_PINNED_MANIFEST_UNQUALIFIED`. Because a self-authored or same-run manifest is **not independent custody**, all outcomes retain 0% physical qualification and operational authority HOLD.

The existing Phase XVIII and XIX freezes are unmodified. No live run, hosted ZIP or independent external custodian was authenticated while authoring this module. Tests are committed, but GitHub-hosted execution remains unverified until real execution logs are acquired and checked.
