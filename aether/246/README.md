# AETHER-246-RS — Credential-free acquirer isolation evidence

An offline, non-authorizing adjudicator for network isolation telemetry, source host pins and acquisition hashes. This module makes NO live network requests. It rejects claimed credential access, missing read-only or namespace isolation claims, failed or missing denial trials, malformed HTTPS endpoints and unbounded acquisition metadata. Input contains only hashes, lengths and declared observations.

Denial categories: loopback, private networks, link-local, cloud metadata, redirects and DNS rebinding. The presence of a `blocked: true` field does NOT prove actual enforcement. A subsequent independently supervised egress test, network namespace inspection, resolver/route review and verified controller custody are still needed.

```bash
python3 -m unittest discover -s aether/246 -p 'test_*.py' -v
python3 aether/246/isolation.py --bundle externally-acquired-isolation-report.json --out hold.json
```

19 offline regression tests passed in the local development environment. GitHub-hosted execution and independently measured isolation are not certified. All output remains `REJECT_OR_UNVERIFIED` with operational HOLD and physical qualification 0%. Earlier phases XVIII/XIX unchanged.

Next bound: AETHER-247-RS isolated egress-denial harness and independently signed measurement receipt, carefully separating measured software isolation from physical operational authority.
