# AETHER-237-RS — Raw Git Tree & Blob Identity

Read-only Git data-identity inspection at an explicitly selected commit.

The verifier retrieves GitHub Git Database API commit metadata, follows the root tree through a bounded path, reconstructs standard Git SHA-1 tree object serialization (including tree sort order), decodes the selected blob, and reconstructs the blob Git object ID. It also checks the blob bytes against an explicitly supplied SHA-256 digest. An observed match only yields `OBJECT_IDENTITIES_MATCH_UNQUALIFIED`.

This does **not** establish immutable timestamps, actual pre-run external custody, independent witnesses, runner authenticity, or physical authority. SHA-1 object identity is not a replacement for independently held SHA-256 or signed pre-run receipt. Gitlinks are deliberately unsupported and fail closed. All authority remains HOLD.

Usage:
```bash
python3 -m unittest discover -s aether/237 -p 'test_*.py' -v
python3 aether/237/git_objects.py --pin-commit <40-hex> --path aether/evidence/pinned-members.json --sha256 <64-hex> --out observed.json
```

Supply real pinned evidence only. Never synthesize an authoritative digest. Phase XVIII and XIX freezes remain unchanged.

Next bound AETHER-238-RS: independently authenticated pre-run custody receipt and replay-resistant timestamp challenge, without ACT promotion.
