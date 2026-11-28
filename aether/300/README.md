# AETHER-300-RS — Signed External Custodian Acceptance and High-Water Reconciliation

AETHER-300 consumes a canonical AETHER-299 handoff packet, verifies its local source-history ancestry with the AETHER-299 audit, and compares an external-custodian-supplied Ed25519 signed acknowledgment to the exact handoff SHA-256 and source journal head/sequence. The signer public key and controller-ancestry graph each require **separately supplied SHA-256 pins**. The declared graph must not share ancestor nodes between journal and custodian roots. The verifier checks a fresh receipt nonce, an explicit claimed remote object identifier and retention-until claim. It checks signature bytes with the Ed25519 verifier already used by AETHER-292.

Accepted receipts are atomically recorded in a new append-only SQLite WAL ledger, with synchronous FULL, a unique receipt nonce, a SHA-256-linked manifest head and a predecessor receipt digest. The recovery auditor verifies every retained canonical manifest, full chain ancestry and nonce uniqueness; can revalidate signatures against the pinned key, reconcile with a supplied original handoff/source journal, and verify an **externally retained high-water sequence/head** if the operator has such a trusted record.

### Boundary

Ed25519 verification proves that a holder of a pinned private key signed the statement. **It does not prove that an independent custodian controls that key**, that the receipt traveled over an authenticated custodian service, that the remote object was actually preserved, or that declared retention dates have elapsed. A source ancestry graph and its pin supplied by the same party are not independent witness evidence. A local copy of a high-water pin can be rolled back with the local ledger. Signed remote acknowledgment claims therefore never release operational authority: HOLD, physical qualification 0%.

The implementation makes no network requests. CLI record requires a **preexisting** externally supplied receipt file and source evidence. Do not create a self-signed receipt and present it as independent custody. GitHub and 0root.ai mirror one owned source ancestry.

### Offline verification

    python3 -m pip install 'cryptography>=43,<47'
    python3 -m unittest discover -s aether/300 -p 'test_*.py' -v

### Signed receipt capture

    python3 aether/300/custodian_acceptance.py record --db /tmp/aether300.sqlite --handoff /tmp/aether299-handoff.json --source-db /tmp/aether297.sqlite --receipt externally-signed-receipt.json --keys independently-pinned-key.json --keys-sha256 <sha256> --ancestry externally-reviewed-ancestry.json --ancestry-sha256 <sha256>

### Reconciliation

    python3 aether/300/custodian_acceptance.py audit --db /tmp/aether300.sqlite --handoff /tmp/aether299-handoff.json --source-db /tmp/aether297.sqlite --keys independently-pinned-key.json --keys-sha256 <sha256> --ancestry externally-reviewed-ancestry.json --ancestry-sha256 <sha256> --external-seq 1 --external-head <sha256>

These tests use ephemeral Ed25519 fixture keys and a mocked prior handoff verification function. They are offline tests, NOT evidence of real remote custody or a provider-side acceptance service.

### Next natural bound — AETHER-301-RS

Read-only external endpoint acquisition of exact receipt bytes, independent controller-key registration proof, retained-object re-fetch under an independently witnessed interval, and explicit source-ancestry confidence labels. Preserve all earlier freezes and HOLD.
