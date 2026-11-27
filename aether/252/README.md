# AETHER-252-RS — Process-Liveness Fencing & Challenge Ledger

Linux read-only sampling uses /proc/<pid>/stat twice around namespace inode read, and incorporates boot ID and process start ticks. This reduces naive PID-reuse ambiguity; it does not guarantee an atomic lifetime snapshot or establish external custody.

The offline adjudicator checks supervisor/worker identities, shared boot, differing namespace inode, append-only event hash chain, nonce duplication, identity binding, previously pinned head claims, and three genuine Ed25519 witness signatures. Tests generate temporary private keys and never commit them.

Run unit tests: python3 -m pip install 'cryptography>=43,<47' && python3 -m unittest discover -s aether/252 -p 'test_*.py' -v

Sample Linux process: python3 aether/252/process_ledger.py identity --pid 1234

Offline review: python3 aether/252/process_ledger.py review --bundle evidence.json --out hold.json

Even when signatures validate, the externally pinned head, independent signer ancestry, process lifetime and durable nonce consumption remain unverified. Every path leaves operational authority HOLD and physical qualification 0%. No earlier freeze is modified.

Next AETHER-253-RS: externally anchored monotone challenge-ledger transitions and process-exit evidence without inferring authority from PID disappearance.
