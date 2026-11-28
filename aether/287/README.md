# AETHER-287-RS — Byte-Exact Export & Custody-Claim Acknowledgment Audit

The AETHER-286 atomic acquisition journal retains complete acquisition manifest preimages. AETHER-287 exports one committed batch to a canonical, exclusive-created, fsynced artifact file. It preserves the exact retained original manifest bytes as base64, the source batch head, parent digest, trust root digest and the three nonce rows. It will not silently replace an existing export.

The read-only audit reconstructs the export against the original local journal and compares three Ed25519-signed acknowledgment statements with the exported artifact digest, head digest and batch ID. It rejects substituted bytes or nonce rows, missing batches, stale/double acknowledgments, invalid signatures, shared controller ancestry (as **declared** in the supplied graph), and conflicting acknowledgment heads.

**Evidence boundary:** A signer can create all three keys, and an operator can self-issue a graph and trust pin. The code does not fetch real external custody receipts or establish the actual ownership or independent physical persistence of an exported artifact. Signatures establish only consistency with the pinned public keys. The nonce history is caller supplied, not externally sealed. An export followed by a real remote custody handoff is a separate workflow not performed here. This preserves the AETHER source ancestry rule: GitHub and 0root.ai mirrors are **one** ancestry, not two witnesses.

Usage:

    python3 -m pip install 'cryptography>=43,<47'
    python3 -m unittest discover -s aether/287 -p 'test_*.py' -v
    python3 aether/287/export_audit.py export --db /tmp/aether286.sqlite --batch 1 --out /tmp/batch-1-export.json
    python3 aether/287/export_audit.py audit --db /tmp/aether286.sqlite --export /tmp/batch-1-export.json --acknowledgments claimed-acks.json --trusted-root-sha256 <64hex>

The exporter uses O_EXCL and fsync as a local durability measure, not permanent immutable object storage. All authority remains HOLD; physical qualification remains 0%. Historical freezes unchanged.

Next natural bound AETHER-288-RS: actual externally retained acknowledgment acquisition with pinned network identities, independent custody proof and durable nonce state readback. No claimed quorum can authorize ACT.
