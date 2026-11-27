# AETHER-272-RS — Persistent Trust Registry & Transcript Replay Fence

A local SQLite registry records three distinct signer/controller claims and public keys before it is sealed. The sealed registry digest is supplied separately during later verification. A bundle of three signed transport statements binds raw byte SHA-256, source and signer, challenge, session ID, and fresh nonces. The verifier checks public-key signatures and inserts the challenge and all three receipts in **one atomic transaction**; any bad signature or reused nonce rejects the entire bundle without consuming a challenge.

The test suite exercises real SQLite persistence across reopened connections, tampered signatures, duplicate sessions, reused challenges, signer substitution, and rollback of partially valid bundles. These are *local* receipts and *locally* pinned public keys. This is not a live HTTPS retriever or an independently administered external registry; the observed source labels and controller ancestry are still unverified.

Run:
    python3 -m pip install 'cryptography>=43,<47'
    python3 -m unittest discover -s aether/272 -p 'test_*.py' -v

Operator commands (use a scratch DB and distinct genuine public-key PEM files):
    python3 aether/272/transcript_registry.py register --db /tmp/aether272.db --key-id k1 --source-id s1 --controller-id c1 --public-key-file k1.pub
    python3 aether/272/transcript_registry.py seal --db /tmp/aether272.db
    python3 aether/272/transcript_registry.py consume --db /tmp/aether272.db --bundle signed.json --trusted-registry-sha256 <64hex>
    python3 aether/272/transcript_registry.py inspect --db /tmp/aether272.db

Registrations cannot change after sealing; the local registry does not guarantee resistance to rollback of the entire SQLite file. Every CLI result deliberately returns exit 1 and authority HOLD. No earlier frozen phase is changed.

Next AETHER-273-RS: independent transcript-byte retrieval, authenticated custody and externally anchored registry monotonicity before treating local signatures as external witness evidence.
