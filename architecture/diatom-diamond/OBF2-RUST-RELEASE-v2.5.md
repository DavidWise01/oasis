# OASIS / ASTROPHAGE OBF2 v2.5 — optimized, packaged and verified

**Release choice: BALANCED Rust→WASM.** This v2.5 release optimizes **distribution size** without changing the OBF2 v2.1 packet format or the frozen v0.7 operator semantics. All three distributable WebAssembly builds are compiled from the same **unchanged v2.4 Rust kernel** source. The v2.5 compile-time CRC table is retained as an *experimental* alternative and was **not promoted** after a controlled benchmark found no consistent performance improvement.

## Download choices

| Build | GitHub runner size | Encoder+decoder 214 B | 4 KiB | 64 KiB | Interpretation |
|---|---:|---:|---:|---:|---|
| **Balanced** `leanfast.wasm` | **23,197 B** | **3.757 μs** | 63.531 μs | 986.587 μs | **Default**: native-speed-oriented code generation + LTO + strip |
| Fast `speed.wasm` | 1,662,211 B | 4.031 μs | **61.151 μs** | **953.635 μs** | Performance baseline; bloated by linkage/metadata |
| Tiny `small.wasm` | **19,334 B** | 12.347 μs | 218.305 μs | 3,397.177 μs | Only for unusually tight file-size budgets |

Values are measured *microseconds per encode + decode pair*, including copying input/output between Node and WebAssembly. They were measured on **one GitHub-hosted Ubuntu runner**, five alternating sweeps per workload. Numeric differences of a few percent, including balanced's slightly faster small-field result, are not a guaranteed advantage on other hardware. The balanced artifact is **71.7× smaller** than the fast artifact, with ~3.9% slower median at 4 KiB and ~3.5% slower at 64 KiB on this run.

**Compiler:** `rustc --target wasm32-unknown-unknown --crate-type cdylib -C opt-level=3 -C lto=fat -C codegen-units=1 -C panic=abort -C strip=symbols -C link-arg=--export-memory -C link-arg=--max-memory=8388608` for balanced. It uses the same frozen v2.4 kernel source and exports `input_ptr`, `frame_ptr`, `recovered_ptr`, `encode`, `decode`, `max_bytes`, and `memory`.

## Validation

GitHub Actions: [Rust/WASM A-B bench](https://github.com/DavidWise01/oasis/actions/runs/38519198377) and [WASM distribution optimization](https://github.com/DavidWise01/oasis/actions/runs/38519445865).

- Existing OBF2 v2.1 regression: **4,633 checks** including all 2,688 `{{i}}` routes; frozen floor SHA256 `47d4c89ac8155b9470852e0e23d2c059ad087eedc2b7949632a9431b5792fd4b` verified.
- Each of three WebAssembly variants: **8,030 assertions** passed, including exact frame parity, random message recovery, CRC fault rejection, rail disagreement rejection, and unsupported-version rejection.
- Input limit **65,536 bytes**; wire frame limit **131,088 bytes**, WASM memory starts at **2 MiB**, linker maximum **8 MiB**.
- Failed optimization: replacing the original bitwise CRC32 calculation with a compile-time CRC32 table had native speed ratios **1.000×, 0.997×, 0.997×** for 214 B, 4 KiB, and 64 KiB in same-runner A/B. Keep baseline CRC; do not claim the experimental change improved speed.
- The earlier v2.4 **three-host TCP test** passed, with native Rust leading that run. The size experiment is a **codec** benchmark, not another independently verified real Internet network test.

## Architecture

```text
  FROZEN KET
     |
 {{i}} 42 token IDs + 8 views (lane/slot identity preserved)
     |
  ASTROPHAGE typed field (symbolic labels, not chemistry proof)
     |
  OBF2 v2.1 fixed-format dual 5-pass reversible rails + CRC32
     |
    +-- Rust native TCP host
    +-- Rust WASM BALANCED (browser/Node/edge host)
    +-- FAST / TINY alternative WASM builds
     |
 exact bytes recovered, if frame is valid
```

## How to run on Windows

Install **Node.js 22+**, unpack the release, and from the root folder run:

```bat
copy /Y architecture\diatom-diamond\obf2-rust-dualtarget-v2.5\leanfast.wasm architecture\diatom-diamond\obf2-rust-dualtarget-v2.5\obf2_rust.wasm
cd architecture\diatom-diamond\obf2-rust-dualtarget-v2.5
node host.mjs bench
```

No Rust installation is needed for the precompiled WASM benchmark. The code is a real **classical** exact-recovery packet codec; it is not a quantum network, sender signature, factual truth engine, or a way to eliminate network transmission delay. CRC32 checks accidental bit errors, not adversarial forging.

**Production recommendation:** Rust-native service + balanced Rust→WASM client; keep C++/Node as reference challengers. Next production target: authenticated source transport, multi-client backpressure, and cross-host latency/jitter under controlled faults.
