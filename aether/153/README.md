# AETHER-153 — Phase X physical reference acquisition setup

**Synthetic commissioning software readiness: 12.5% (turn 1/8). Empirical physical qualification: 0%. Real operational authority: HOLD.**

An exact locally executed Python test ran **25 seeds × eight acquisition scenarios × 20 ticks = 200 episodes / 4,000 decisions per policy**, passing **3,200/3,200 deterministic gates**. Baseline signed-only admission had **1,200 unsafe synthetic ACT**; setup-gated admission had **zero**, preserving **2,800 safe dry-run ACT**, including **500/500 clean** and **500/500 legitimate reference rotation**.

The fail-closed setup contract requires DUT/reference equipment serials, certificate provenance, calibration expiry, raw sample capture SHA-256, bound measurement path, matched challenge and conservative risk envelope. Fault scenarios include missing serial, untrusted laboratory, expired certificate, absent raw capture, path unverified, and challenge mismatch. Policy receives signed mock receipts, not hidden simulated truth.

**The physical setup has NOT happened:** equipment identity, traceable reference standard, actual raw samples, calibration and path-coupling fields are deliberately null in [physical_setup_register.json](physical_setup_register.json). The mock issuer string and HMAC are not proof of accreditation or metrological traceability. Actual independent measurement count = 0.

The full executed local Python has SHA-256 `e61bcff26a003ae570a8279b57f45709e15fabb42cd1ad285a250db14e9a069b`, and is included with complete 3,200 checks, seed results and append-only SHA-256 traces in the downloadable ZIP. GitHub `experiment.py` is a distinct compact reproducer, not yet independently executed; Pages deployment likewise unverified.

Next AETHER-154: physical reference equipment identity and certificate intake, accepting genuine evidence if supplied but never fabricating measurements or changing operational HOLD.
