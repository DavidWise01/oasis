# AETHER-235-RS — Manifest Ancestry & Cross-Run Binding

Phase XX follow-on to the AETHER-233 acquisition probe and AETHER-234 ZIP-member verifier.

**Status:** internal-consistency review authored; no live execution evidence or independently authenticated manifest custody acquired; physical qualification 0%; operational authority HOLD.

This bound records a manifest SHA-256, source commit SHA, pinned-manifest commit SHA, exact repository/path, run ID, and an ancestry claim. It detects contradictory assertions and always rejects authority: an `api_confirmed: true` field in supplied JSON is not proof of an authenticated API response, and a supplied external receipt is not a verified signature.

It explicitly detects self-run or post-run pinning risk. A future independent verifier must retrieve actual Git commit objects, establish strict ancestry using the Git commit DAG, authenticate the pin's pre-run timestamp with external custody and witness ancestry, and bind downloaded GitHub-hosted bytes to the manifest. GitHub timestamps and JSON fields alone cannot certify real-world time or independent custody.

Run:
```bash
python3 -m unittest discover -s aether/235 -p 'test_*.py' -v
python3 aether/235/manifest_ancestry.py --evidence actual-snapshots.json --out review.json
```

All outputs fail closed. Do not fabricate a run, receipt, manifest, or witness. Earlier freezes remain unchanged. No destructive operation, repair, lock recovery, or physical ACT is authorized.

Next natural bound: AETHER-236-RS, authenticated remote commit-DAG retrieval with raw response hashes, pagination and adversarial ancestry coverage.
