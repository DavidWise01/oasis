# AETHER-243-RS — External Evidence Acquisition and Source Ancestry

Read-only, bounded HTTPS acquisition of externally located evidence bytes using explicit exact host allowlists and pre-pinned expected SHA-256. The verifier records hash, length and claimed controller without including the body. It rejects mismatched digests, repeated bodies, shared controller labels, invalid URLs, failures and redirects.

**Operational limitation:** hostname allowlisting by itself does not protect against DNS rebinding or all server-side request forgery. Only enable real retrieval in an isolated environment with egress restrictions, resolver pinning, no access to internal networks and independent review of source URLs. This phase does NOT certify remote host identity beyond ordinary transport, independent controller ancestry, external custody, authenticated UTC or physical capture. All results explicitly HOLD.

```bash
python3 -m unittest discover -s aether/243 -p 'test_*.py' -v
python3 aether/243/source_acquisition.py --config externally-pinned-input.json --out acquisition.json
```

The tests are offline mocks, not external evidence acquisition. Source publication alone does not establish execution. Phase XVIII/XIX freezes remain unmodified.

Next AETHER-244-RS: independent source-ancestry challenge with externally held signed attestations, replay protection and verified network isolation. Maintain 0% physical qualification and operational HOLD.
