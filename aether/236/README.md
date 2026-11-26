# AETHER-236-RS — Git Commit-DAG API Readback

A bounded read-only traversal of GitHub's actual `git/commits/{sha}` API. Every returned response is hashed, each requested SHA is checked against the returned SHA, parent links are checked, and strict ancestor traversal is bounded by 256 nodes and 128 depths.

This is *not* native raw Git-object SHA reconstruction, independent custody, verified commit creation time, or physical qualification. A successful result is strictly `STRICT_ANCESTOR_OBSERVED_UNQUALIFIED`, never ACT. Errors, incomplete retrieval, and missing ancestors fail closed. No changes to Phase XVIII/XIX freezes.

```bash
python3 -m unittest discover -s aether/236 -p 'test_*.py' -v
GITHUB_TOKEN=... python3 aether/236/git_dag_readback.py --pin-commit PIN_40_HEX --run-head HEAD_40_HEX --out dag-observation.json
```

This only establishes API-reported ancestry if supplied pins and head are actual reachable objects. It does not determine that the manifest was already present at the pin commit. To establish that, inspect the exact file tree/content at the pin commit and externally authenticate its timing and custody; Git commit timestamps alone are not authoritative.

**Next boundary AETHER-237-RS:** retrieve raw Git trees and blob content at pinned commits; bind the expected manifest to actual Git-object hashes and a separately held, pre-run receipt. Operational authority remains HOLD.
