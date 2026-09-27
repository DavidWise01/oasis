# Frozen Primitive Stress Boundary — 2026-09-27

## Frozen primitive

```text
+{-{ .16 .16 .1 .1 .0 .0 .1 .1 .16 .16 }+}-
```

Transform invariant:

```text
P = [(.)]
T(P) = mir(rev(upsidedown(inversed(P))))
T(P) ≅ P
```

## Confirmed exact streaming result

- Candidates checked: **268,435,456 (2^28)**
- Chunk size: **8,388,608 (2^23)**
- Chunks completed: **32**
- Primitive mean throughput: **31,857,300 candidates/s**
- Primitive minimum throughput: **22,457,846 candidates/s**
- Primitive maximum throughput: **33,801,707 candidates/s**
- Reference mean throughput: **33,233,298 candidates/s**
- Parity failures: **0**
- Witness failures: **0**
- First kernel failure: **none**
- Digest: `61656e53696a1876564bc56753a053036ee3acf32c597e210af2f9031b571e77`

## Next-level attempts

Target **2^30 = 1,073,741,824** streamed candidates was attempted first. The notebook execution environment interrupted the run at its wall-clock ceiling before completion.

The same workload was retried outside the notebook. The container execution wrapper also terminated before completion.

Target **2^29 = 536,870,912** was then attempted as the largest exact intermediate checkpoint likely to fit. The container wrapper again terminated on its execution-time limit before completion.

## Failure classification

```text
correctness          PASS through 2^28
shadow witness       PASS through 2^28
streaming memory     PASS through 2^28
throughput collapse  NOT OBSERVED
kernel failure       NOT OBSERVED

first current limit:
EXECUTION-HARNESS WALL CLOCK
```

The 2^29 / 2^30 attempts must **not** be recorded as primitive failures because no parity or witness divergence was observed. They are incomplete runs caused by the benchmark host.

## Next reproducible target

Run the same chunked benchmark on an unrestricted local runtime until one of these occurs:

1. full 2^29 completion,
2. full 2^30 completion,
3. parity failure,
4. witness failure,
5. memory/allocation failure,
6. sustained throughput collapse.

No biological-efficacy claim is implied by this benchmark; it measures deterministic sequence-comparison software parity and throughput.
