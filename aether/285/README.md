# AETHER-285-RS — Complete Acquisition-Chain Replay & High-Water Prefix Audit

This read-only phase reconstructs the AETHER-284 acquisition batch SHA-256 chain and nonce history from SQLite plus **preserved external manifests**. The AETHER-284 database records each witness's key ID, raw body digest, observation digest, and nonce, but NOT the requested URL. Therefore the stored rows alone cannot reproduce the original hash: the verifier requires an out-of-band preserved per-batch manifest containing the original requested URL alongside the original raw/observation digests.

The auditor detects deleted or reordered batches, broken parent hashes, changed raw/observation digests, replaced endpoint URLs, duplicate/replayed witness nonces, missing nonce triples, shortened high-water history, and substituted historical heads. A separately supplied canonical SHA-256 of an anchor is required. Matching an anchor pin means consistency with that pin; no independent archive ownership, signed custody, or remote anti-rollback service has been demonstrated.

Because the original AETHER-284 batch code does not export the complete preimage as an artifact, collecting the manifests requires a trusted acquisition-side log or reconstruction with provenance. Do **not** invent missing URLs or label a reconstructed manifest as acquired evidence. This phase does not mutate AETHER-284 or historical freezes.

Tests:
    python3 -m unittest discover -s aether/285 -p 'test_*.py' -v

Read-only audit:
    python3 aether/285/acquisition_replay.py --db /tmp/aether284.sqlite --manifests acquired-batch-manifests.json --anchor separately-retained-anchor.json --trusted-anchor-sha256 <64hex> --out audit-hold.json

No operational ACT is authorized; physical qualification remains 0%.

Next AETHER-286-RS: capture original manifest preimages at the moment of AETHER-284 acquisition in the same atomic transaction, then externally witness high-water retention without conflating mirror ancestry.
