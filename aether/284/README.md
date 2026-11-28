# AETHER-284-RS — Raw Witness Acquisition and Persistent Nonce Fence

This phase connects AETHER-264's bounded, DNS/IP-vetted TLS HTTPS collector with AETHER-283's prefix-witness verifier. It fetches three explicitly mapped witness URLs using host allowlists, verifies the raw body bytes and transport observation SHA-256, compares all Ed25519 signed prefix claims with the original AETHER-282 historical checkpoint, checks the caller-provided out-of-band trust-record digest, then atomically stores all witness nonces and a SHA-256-linked acquisition batch in a separate local SQLite database.

The caller must explicitly invoke the capture CLI with an authorized live endpoint mapping and a challenge nonce. The regression suite uses mocked network records and real Ed25519 signatures. A reused challenge nonce, previously committed witness nonce, changed transport observation, bad source signature, common endpoint host, or conflicting historical prefix rejects the whole acquisition, leaving no partially consumed nonces.

Limits: TLS authentication and a signature prove neither three distinct controllers nor immutable external custody. The graph and trust digest are supplied by the operator; local nonce persistence can be rolled back with the file. AETHER-283 reports these custody limits explicitly, and AETHER-284 never removes them. The acquisition-batch SHA chain is a local integrity aid, not externally anchored anti-rollback.

Run:
    python3 -m pip install 'cryptography>=43,<47'
    python3 -m unittest discover -s aether/284 -p 'test_*.py' -v
    python3 aether/284/acquire_witness.py capture --db /tmp/aether284.sqlite --journal /tmp/aether282.sqlite --trust-record trust.json --trust-sha256 <64hex> --endpoints endpoints.json --challenge-nonce <freshnonce>
    python3 aether/284/acquire_witness.py inspect --db /tmp/aether284.sqlite

The earliest freezes and all previous phase directories remain unchanged. Operational authority HOLD. Physical qualification 0%.

Next AETHER-285-RS: independently retained nonce seal readback and verified acquisition-batch chain, with explicit provenance of remotely preserved witness bytes.
