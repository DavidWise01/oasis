# AETHER-250-RS — Namespace Snapshot & Signed Observer Receipt

The read-only collector samples the **current process namespace inode** and the exact bytes of Linux /proc/net/route, /proc/net/ipv6_route and /proc/net/dev. It also lists interface names. The output stores bounded base64 bytes, byte lengths, SHA-256 digests, and a deterministic snapshot digest. It never opens sockets, changes a namespace, or executes an OS command.

The verifier checks raw bytes, schema, binding, and genuine Ed25519 signatures against a separately supplied public-key record. Tests generate temporary keys for local cryptographic correctness. The verifier does not authenticate that record's provenance; a caller can manufacture both keys and bytes. **Observing an inode or interface does not itself establish that isolation was enforced**, nor prove egress denial, independent custody, or trusted UTC.

Install cryptography and run tests:

    python3 -m pip install 'cryptography>=43,<47'
    python3 -m unittest discover -s aether/250 -p 'test_*.py' -v

Collector (Linux only): python3 aether/250/namespace_observer.py collect --out observation.json

Review: python3 aether/250/namespace_observer.py review --bundle signed-bundle.json --out hold.json

All CLI paths exit nonzero; observation cannot grant operational ACT. Frozen historical phases are untouched, physical qualification remains 0%, and operational authority HOLD.

Next AETHER-251-RS: binding supervisor and worker namespace evidence in one fresh challenge with independent signer provenance and replay detection, while retaining HOLD.
