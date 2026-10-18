# Z338 — Tritrioctium (Tto): clean-checkout acceptance gate

Date: 2026-10-18. Experimental symbolic-computational registry only. No physical element discovery.

## Source basis
All six Z328-Z333 scripts were fetched from GitHub at pinned revision `7afe006ea81adc2952c682d176d949c29b39c5f2`. Their Git blob identities match the expected values embedded in Z337 consolidated runner.

## CI setup
Added `.github/workflows/mn-prime-z338.yml` at commit `254b0fc60729a11514e639e376c164228af3c8c3`. The workflow uses GitHub checkout, Python 3.12 and cryptography, then runs `python research/mn-prime/experimental-cipher/z337/run_recovery_suite.py`. It is configured for push events affecting its path or experimental registry paths, plus manual workflow_dispatch.

## Acceptance status
- Source presence / pinned blob hashes: VERIFIED through GitHub connector.
- Earlier local six-suite regression: 115/115 PASS, but some local copies differed from repository versions.
- Clean-checkout GitHub CI **result not yet confirmed** (connector lacks a general workflow-run discovery endpoint in this session; commit-run lookup filters PR-triggered runs).
- **Freeze not granted**; no tag, signed release, protected reference or immutable release archive created.
- Even a passing CI run is not a production security certification or physics evidence.

The frozen KET core and optional Cr24 / RGB research overlays remain unchanged.

Next: observe actual CI outcome, resolve any failing checks, then pin an accepted release reference rather than creating more speculative layers.
