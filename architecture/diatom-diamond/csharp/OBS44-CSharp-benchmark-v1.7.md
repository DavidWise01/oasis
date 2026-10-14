# OBS44 C# / .NET 10 real compilation and throughput report

**Status: PASS** — [GitHub Actions run 38491363245](https://github.com/DavidWise01/oasis/actions/runs/38491363245), commit `c49423aa4cf05e49cfd699e7a4232238ebbb117c`. Workflow: `.github/workflows/obs44-csharp-benchmark.yml`.

## Configuration
- Host: one ephemeral GitHub-hosted `ubuntu-latest` runner, 2026-10-14 UTC.
- C#: .NET **10.0.13** running `net10.0` Release; project `csharp/Obs44Bench/Obs44Bench.csproj`. `TreatWarningsAsErrors=true`.
- JavaScript: Node.js **v22.23.3**, executing the original v1.2 OBS bus behind the 44-address adapter.
- Same ordered 44-glyph registry (`00=n`, `43=.0x`), 32 tokens per frame, 20,000 tokens, 625 frames. Both sides execute the dual five-pass `UUDDLRLRBASS` transformation, OBS coordinate encode/decode, and exact recovery.
- Both benchmark commands warm up, then run five timed iterations sequentially on the same runner. These are **symbolic glyphs/s**, not neural-model inference.
- All GitHub Actions jobs and steps succeeded; C# in-process checks: **226 assertions**, 0 failures.

## Measured results

| Measurement | Result |
| --- | ---: |
| C# median throughput (5 runs) | **3,748.1977259759365 glyphs/s** |
| Node.js median throughput (5 runs) | **4,334.154161597853 glyphs/s** |
| C# difference vs Node.js | **-13.52%** |
| Node.js speed advantage vs C# | **15.63%** |
| C# run durations (s) | 5.5626, 5.3114, 5.3359, 5.3657, 5.2888 |
| C# cumulative managed allocation (20,000 glyphs, typical run) | **589,342,352 B (562.04 MiB)** |
| C# cumulative allocation per glyph | **29,467 B** |
| C# bounded-channel stream (different token workload) | **5,197.827630315841 tokens/s** |
| C# stream exact recovery | 20,000 / 20,000 |
| C# stream frames | 625 |
| C# stream max generated lead | 65 |
| C# stream channel capacity | 1 frame |

### Interpretation
- **Do not switch to C# solely for speed yet.** Node wins on this exact paired workload, and 5 runs are not comprehensive profiling.
- The C# streaming figure is **not comparable** to the paired 44-address glyph benchmark: it uses a separate `ObsStreaming.TokenAt` generator and bounded asynchronous channel.
- Cumulative managed allocation is **not** peak heap or physical RSS.
- The current C# code repeatedly allocates decimal strings for exact `BigInteger` OBS coordinates, including large mirrored coordinates near `10^3000`. Profile this work before refactoring.
- **Optimization proposal:** keep the frozen 5-pass semantics and the exact OBS coordinate codec, but use `byte` glyph IDs (0..43) and fixed-size span/array permutations in the hot path; defer `BigInteger` expansion and mirror materialization until external serialization/inspection. Maintain full parity tests, including `n=00` and atomic `.0x=43`. Compare again on the same hardware after optimization.
- For a production choice, test Windows 11, repeat longer samples, measure GC/allocated bytes, peak RSS and p95 latency, and benchmark actual TCP mode separately. No C# TCP wire-equivalence is claimed here.

## Reproduce
```bash
cp architecture/diatom-diamond/csharp/ObsAddress44-v1.6.cs architecture/diatom-diamond/csharp/Obs44Bench/ObsAddress44.cs
dotnet build architecture/diatom-diamond/csharp/Obs44Bench/Obs44Bench.csproj -c Release
dotnet run --project architecture/diatom-diamond/csharp/Obs44Bench/Obs44Bench.csproj -c Release --no-build -- --bench44 20000 5
dotnet run --project architecture/diatom-diamond/csharp/Obs44Bench/Obs44Bench.csproj -c Release --no-build -- --stream 20000 0
node architecture/diatom-diamond/csharp/Obs44Bench/obs44-node-bench.mjs 20000 5
```

The frozen `v0.7` floor was not modified.
