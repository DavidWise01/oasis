# AETHER-282-RS — Original Challenge Retention and Historical Prefix Replay

A new single-database journal retains the exact canonical original challenge JSON in the **same transaction** as its three Ed25519 signed receipts and chained checkpoint. Unlike AETHER-280, which stores only the challenge digest, this schema enables a read-only restart auditor to reconstruct the original signed statements, verify every persisted Ed25519 signature, and detect changed original challenge JSON or payload digest.

Each SHA-256 chained checkpoint may be compared against a separately supplied historical prefix sequence and digest. This works even when the local journal is later extended: an older checkpoint must remain present at its original sequence index. That is a stronger check than comparing only the latest head to a historical last-head pin.

No live external challenge custody is established by the CLI parameters. The caller-provided prefix could be fabricated or rolled back with the local database; public keys may represent one controller; no operational ACT is permitted. This is an isolated new journal design, not a migration of historical AETHER-280 files.

    python3 -m pip install 'cryptography>=43,<47'
    python3 -m unittest discover -s aether/282 -p 'test_*.py' -v
    python3 aether/282/retained_journal.py bootstrap --db /tmp/aether282.db --keys signers.json --pin <64hex>
    python3 aether/282/retained_journal.py append --db /tmp/aether282.db --bundle bundle.json --pin <64hex> --expected-head <64hex>
    python3 aether/282/retained_journal.py audit --db /tmp/aether282.db --prefix-seq 1 --prefix-sha256 <64hex>

Physical qualification 0%; operational authority HOLD. Earlier phases and freezes unchanged.

Next AETHER-283-RS: independently acquired immutable prefix custody and crash-interruption evidence for retained signed statements, with no assumed independent quorum.
