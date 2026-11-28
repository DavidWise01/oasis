# AETHER-278-RS — Local High-Water Checkpoints & Multi-Restart Forensics

A bounded, persistent SQLite ledger stores successive registry, challenge, receipt, and rotation high-water counts as a SHA-256 linked history. Every append is guarded by BEGIN IMMEDIATE, an expected prior-head digest, strictly increasing sequence number, nondecreasing counters, and receipt conservation (three receipts per challenge). A registry digest cannot change without the recorded rotation count increasing.

The audit reconstructs the SHA-256 history and compares it against a **caller-supplied** signed checkpoint whose digest must also be provided as a separate command-line pin. It detects missing high-water sequence numbers, replaced historical heads, reduced challenge/receipt/rotation counts, invalid signatures, and altered links. A signed anchor proves only consistency against the presented public key; no external custodian or authenticated high-water service has been observed. SQLite files can still be replaced wholesale. The authority gate remains HOLD with 0% physical qualification.

Run:
    python3 -m pip install 'cryptography>=43,<47'
    python3 -m unittest discover -s aether/278 -p 'test_*.py' -v
    python3 aether/278/highwater.py append --db /tmp/aether278.db --registry-sha <64hex> --challenges 1 --receipts 3 --rotations 0 --run-id 278 --expected-head <64zeros>
    python3 aether/278/highwater.py inspect --db /tmp/aether278.db
    python3 aether/278/highwater.py audit --db /tmp/aether278.db --anchor anchor.json --trusted-anchor-sha <64hex>

These are separate local custody records, not synchronized automatic checks of AETHER-276's underlying database. For meaningful reconciliation, counters must first be independently read from the original ledger and verified. Frozen phases remain unchanged.

Next AETHER-279-RS: cross-database snapshot atomicity and externally preserved high-water evidence, with explicit independent-source ancestry requirements.
