# AETHER-248-RS — Raw Probe Transcript Capture

Captures six exact local transcript files (loopback, private, link-local, metadata, redirect, DNS rebinding) without executing a process or sending network traffic. Bounds each raw file at 64 KiB; rejects symlinks, unsafe file names, bad source IDs and incomplete categories. Review reconstructs SHA-256 hashes and snapshot integrity.

A matching SHA-256 only verifies fidelity to the local snapshot. No network isolation, denial event, independent witness, UTC authenticity, or external custody is proven. Self-created fixture transcripts are not a live probe. All review reports say REJECT_OR_UNVERIFIED, with 0% physical qualification and authority HOLD.

Run offline tests: python3 -m unittest discover -s aether/248 -p 'test_*.py' -v

Capture: python3 aether/248/raw_probe.py capture --spec spec.json --folder transcripts --out snapshot.json

Review: python3 aether/248/raw_probe.py review --snapshot snapshot.json --out hold.json

The command intentionally exits nonzero even for coherent input. Historic Phase XVIII/XIX freezes unchanged. Next AETHER-249: supervised restricted-network execution with actual socket outcomes, independently retained raw transcripts and authenticated signatures.
