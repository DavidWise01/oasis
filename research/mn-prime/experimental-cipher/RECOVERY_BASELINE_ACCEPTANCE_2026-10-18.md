# MN PRIME / OCTAVIA — Experimental Recovery Baseline Acceptance

Status: **ACCEPTED / FROZEN RESEARCH BASELINE** (software-only scope)
Date: 2026-10-18

## Independently verified GitHub Actions evidence

Workflow: `.github/workflows/mn-prime-z338.yml`, **MN PRIME Recovery Acceptance**.

1. Reset-commit run [39139252468](https://github.com/DavidWise01/oasis/actions/runs/39139252468)
   - Head SHA `74fa6ab6b0c3641a870172af3087729dd88ec77d`
   - Completed successfully, acceptance job `117710080426`
   - Job log explicitly states `PASS Z337 115/115 verified checks`
   - Artifact `mn-prime-recovery-acceptance` ID `12141146407` (present, unexpired when checked)
2. Repeated run [39140494507](https://github.com/DavidWise01/oasis/actions/runs/39140494507)
   - Head SHA `66c084e964502b4ef3285c66a45154bf8591ab06`
   - Completed successfully, acceptance job `117713755473`
   - Job log explicitly states `PASS Z337 115/115 verified checks`
   - Artifact `mn-prime-recovery-acceptance` ID `12141551060` (present, unexpired when checked)

Both logs individually report:
- Z328 20/20 source `3a7629b27bd2aca0baecf10f4c06bf044dae8fda`
- Z329 20/20 source `f8660f47fe59d7840a2aeb938542dfd330e045dd`
- Z330 20/20 source `f2f5b358811af574823a0c7c1cbba57ce0238f92`
- Z331 20/20 source `f8d1c07beb7fcac0faf4299b1743e8c018419b15`
- Z332 15/15 source `fbadfd2d27ced597b0b5d96fd661490cfd93c748`
- Z333 20/20 source `c794be8182a7e98360a63173f297d4ff98434afc`

## Accepted scope
Freeze the **experimental software recovery substack** consisting of six tested modules and Z337 runner pinned to the above exact Git blob SHA identities. The later accepted checkout commit `66c084e964502b4ef3285c66a45154bf8591ab06` is an audit reference; other unrelated repository changes exist in that commit history and are not certified by this test.

This is a *documented research baseline freeze*, not a protected Git branch, signed tag, GitHub Release, or immutable artifact repository; no such infrastructure has been created. No changes to frozen KET kernel.

## Exclusions / cautions
- Local cryptographic simulations and SQLite rollback tests are not equivalent to cross-host independent witnessing, actual power-failure durability, secure production key management, live revocation services, or certified security.
- Z330 fixed test private keys must never be deployed as secrets.
- GitHub logs contain Node.js 20 deprecation warnings for actions/checkout@v4, setup-python@v5 and upload-artifact@v4 forced onto Node.js 24. Warnings did not fail the jobs; upgrade Actions in a separate non-baseline change.
- This research model does not establish a real element with atomic number >118 or validate physics/quantum claims.

## Disposition
**Research acceptance complete. Stop cyclic Z-number advancement for this substack.** Any new work must occur on an explicitly separate unfrozen branch/track; do not mutate accepted source modules under the claim of the same baseline.
