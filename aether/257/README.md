# AETHER-257-RS — Externally Claimed CAS Ledger and Split-Brain Fence

Read-only adjudicator for competing ledger-write attempts on multiple hosts. Reconstructs recorded compare-and-swap decisions sequentially from a caller-provided anchor. Detects accepted writes against stale heads, duplicate accepted challenges and nonces, nonmonotonic sequence numbers, altered decision records, rejected writes that change the head, and inconsistent three-witness journal claims.

This checks a representation of CAS transitions; it does not execute an atomic CAS against external immutable storage or verify that a server serialized two requests. The anchor and witnesses are untrusted input. Three distinct labels do not establish controller independence. No cryptographic key ancestry or signature validation is claimed in this module; prior phases handle signature verification. Never infer successful external coordination from this result.

Run locally:

    python3 -m unittest discover -s aether/257 -p 'test_*.py' -v
    python3 aether/257/cas_fence.py --bundle claimed-ledger.json --out hold.json

All outcomes remain REJECT_OR_UNVERIFIED; physical qualification 0%, operational authority HOLD. No historic freeze changed.

Next AETHER-258-RS: competing-host CAS concurrency harness with an actual durable compare-and-swap primitive and independently acquired, signed transaction receipts. Local synthetic races remain noncertifying.
