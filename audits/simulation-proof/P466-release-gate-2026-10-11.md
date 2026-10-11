# ROOT0 P4.66 — deterministic security regression gate (2026-10-11)

**Local PASS: 42/42 inherited assertions** (P4.65 19/19; P4.64 15/15; P4.46 8/8), Node 22.16.0. A new runner (`docs/reality-tensor/dyson-inversions/p466_gate.mjs`) executes all three tests using independent child processes, checks process exit status, parses PASS and exact expected assertion count, and fails closed if a suite is absent, times out, fails or falsely claims independent-host validation. Results stored as machine-readable JSON. This is 42 *existing* assertions, not 42 new test cases. The run is local; hosted CI was not observed.

**Prototype completion remains 15/20=75%.** Hosted GitHub Actions has not been confirmed green; independent remote custody remains unverified. The committed runner requires tests and dependencies which are packaged with the downloadable ZIP but not yet all published in the repository. It cannot currently be called a successful clean-checkout CI job.

Complete reproducible ZIP SHA-256 `43798b219d3e6c2e062b0dc36ed9ed180663498415e6b03b4810c28689f7635f` contains all three test suites and dependencies.

Next P4.67: sync missing regression dependencies into GitHub, wire workflow, verify hosted execution, then re-evaluate CI milestone.