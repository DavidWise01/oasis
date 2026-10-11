# ROOT0 K.E.T. R0 — Source Freeze Manifest

Freeze date: 2026-10-11
Architecture: `{{ | K | {{ | E | {{ | T }} }} }}`
Operators: `i = intent`, `u = understanding`
Temporal scope: past / present / future

## Immutable source snapshot (GitHub blob SHA-1)

```
docs/reality-tensor/dyson-inversions/p443_atomic.mjs    0456626f828095387bed0c238d45b392b3bdce95
docs/reality-tensor/dyson-inversions/kernel0.mjs         3b38ba0e6b3681ceae25bfe059e3a7649100b727
docs/reality-tensor/dyson-inversions/ket.mjs             48ca3b120b1766f26ae4c4a4fd5b7f3f756d6299
docs/reality-tensor/dyson-inversions/test_ket.mjs        84d5fb6c92b854b106e451aa639cbefbe03501bf
docs/reality-tensor/dyson-inversions/test_kernel0.mjs    fe4819e98f9c773862423eefbeeb603314fc5438
docs/reality-tensor/dyson-inversions/release_gate.mjs    1ead085faf79701cd9567301fab97b340a6f7303
```

The missing `test_kernel0.mjs` was committed (commit `b3fd60f97ff87dedb6198b2f84f41d402ad06ed8`) and all six GitHub file paths/blob identifiers were fetched successfully.

## Evidence

A dependency-isolated temporary tree extracted from the prior release ZIP ran `node release_gate.mjs` on Node v22.16.0 and reported **PASS 24/24** (KET 13/13 and KernelZero 11/11). **This was NOT a true clean git clone of the exact GitHub blobs:** `git ls-remote https://github.com/DavidWise01/oasis.git HEAD` failed due to unavailable DNS to github.com from the execution container. Historical ZIP file bytes also do not match all recorded GitHub blob IDs. Therefore byte-exact clean-checkout regression, GitHub-hosted CI, and complete R0 release-qualification remain **UNVERIFIED**.

## Freeze decision

**Source/interface freeze: YES (manifest above).**
**R0 qualification / production release: NO-GO until exact committed-source clean clone and mandatory CI succeed.**

Do not change the six frozen files silently; any change creates a new explicitly versioned manifest and resets verification. Historical other kernels remain unmerged archives.

## Required external verification

```bash
git clone https://github.com/DavidWise01/oasis.git
cd oasis/docs/reality-tensor/dyson-inversions
node --version # requires Node 22
node release_gate.mjs # must show PASS and 24/24
```

Verify each frozen Git blob against the list in this manifest with `git hash-object <file>`. Record full checkout commit SHA and hosted CI run URL. Only then change the R0 clean-checkout status.
