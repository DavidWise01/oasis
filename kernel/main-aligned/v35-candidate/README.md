# Lean kernel integration checkpoint v35 (candidate)

**This is not a full Lean certification of the OaSIs kernel.** The frozen
parent remains untouched. The current main aligned trunk is v34, and its
compressed transport is legacy until promoted separately.

## Implemented formal contracts
- verified-only candidate promotion; quarantine/non-aligned cannot advance
- two-register history carry-forward
- a reversible register with round-trip theorem
- append-only witnessed event log with history and length proofs
- crawler -> git -> agentic -> post finite stage progression
- literal root-token stability (software constant only)

## Verify

```sh
lean --version
lean lean/OasisKernelIntegrationV35.lean
```

The GitHub Actions workflow `.github/workflows/lean-kernel-integration.yml`
runs this source with Lean v4.33.1. **A successful run of that workflow is
required before describing this file as Lean-compiled.**

## Explicitly not yet certified
- v34 full monolithic source and its older compressed transport
- all archived Lean modules and frozen v92/v111 artifacts
- behavioral equivalence between WASM/I13/toroidal/1-bit/AE runtimes and Lean
- 8D floating-point Givens fixture numerics; the formal register is abstract
- end-to-end executable production boot and deployed CI

Never replace the frozen canon or claim 0e for full kernel based on this module.
