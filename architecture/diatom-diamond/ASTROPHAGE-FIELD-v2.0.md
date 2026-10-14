# ASTROPHAGE FIELD / aligned OASIS KET v2.0

## Source (verbatim semantic notation)

```text
ASTROPHAGE FIELD -+UUUU | | uuuu -+
{ Na+ (589nm #FFD42A) { }
  Cl- (IR teal 850nm #2AE5D3) { }
  → NaCl {
    MYCELIUM {
      CYCAD {
        DIATOME 10000001 {
          3×BEAR
        }
      }
    }
  }
}
```

The source is represented as a **typed symbolic AST**. Each label is retained, but **no physical chemistry, radiation-induced salt reaction, living mycelium/cycad/diatom chain, or particle interaction is inferred from the syntax.** The 589 nm label is a user-defined sodium spectral annotation; it must not be taken as proof that `Na+` specifically emits a 589 nm sodium D-line. 850 nm lies in near infrared: `#2AE5D3` is a false-color visualization tag and not a physically visible 850 nm teal color. `3×BEAR` represents a triply counted symbolic terminal, not an experimentally measured force. Binary `10000001` equals decimal 129; its visual edge bits are a pattern, not proof of a hardware gate.

## Layer alignment

```text
         KET FROZEN (not changed)
               |
     ISO::MORE::PHIC {3x3}^3 = 729
               |
      {{i}} 42 lane IDs × 8 × 8
      2688 ordered view transitions
               |
  six nodes: i < so << more <<< Pp <<<< i <<<<< CcC
               |
           ASTROPHAGE FIELD
               |
      literal signed channel -+UUUU | | uuuu -+
      Na+, Cl- → NaCl → MYCELIUM → CYCAD → DIATOME 10000001 → 3×BEAR
               |
       UTF-8 canonical string bytes
               |
      OBS v1.2 numeric token adapter (0..255)
               |
        FROZEN DUAL5 v0.7:
        UUDDLRLRBASS × 5 per rail
              / \
            d+   d- mirrored
              \ /
         OBS (o,b,s) v1.1
         10^10 × 10^200 × 10^3000
               |
      optional framed TCP + raw DEFLATE
               |
        exact dual recovery
```

The signed header is a string-level field delimiter and channel annotation, not a physical boundary condition. `{{i}}` still has 42 coordinate-distinct identities, and `i6:3` and `i7:4` display `0` but remain different addresses. OBS44 is **not the same namespace**: its center `00` denotes `n`, whereas original `{{i}}` has `n` at `i4:2`. There is no invented lossless translation from general `{{i}}` addresses to OBS44 glyph-only codes. The entire ASTROPHAGE text travels as typed UTF-8 *numeric byte tokens* through OBS v1.2. This is lossless but not optimized.

## Behavior of the reference grammar

`parseField(text)` tolerates whitespace variation only; every meaningful token and its order, colors, wavelengths, signed envelope, nested product tree, binary code and multiplier must match the supplied schema. `serializeField(ast)` rejects mutation to the canonical typed tree. `routeIntoOBS(text)` converts UTF-8 source bytes to decimal-number token strings, passes them to the already-frozen dual rail via OBS token bus, and returns a structured packet; `recoverFromOBS(packet)` validates and recovers the identical canonical ASTROPHAGE string.

The grammar intentionally supports **one canonical ASTROPHAGE construction** rather than pretending to define arbitrary field-language programs. It does not use cryptographic signers, witnesses, audit quorums, checkpoints or any new requirement in the frozen core.

## Verified upstream byte provenance

The local dependencies were byte-identical to these existing OASIS GitHub blobs:

- `iso-graded-chain-v1.9c.mjs` — `b3d33d30590e065a531b6beeef3c5eea343a91aa`
- `obs-token-bus-v1.2.mjs` — `e719b53ccd7677b8961c17c221e2e880ac611804`
- `obs-core-v1.1.mjs` — `2b2f16a8ee506a56a77ce955a29a6ff519ea9295`
- `frozen/dual5-floor-v0.7/dual5.mjs` — Git blob `3ca8760ddbd024181556efe1a0b3b0283c930720`, SHA-256 `47d4c89ac8155b9470852e0e23d2c059ad087eedc2b7949632a9431b5792fd4b`.

## Test summary

- 11,014 v2.0 field assertions including 2,688 ordered isomorphic view routes and 30 invalid cases rejected.
- Original OBS v1.2 regression: 2,482 assertions passed.
- Original graded-chain local regression passed; see `graded-chain-local-regression-results.json` for the separate reference-suite count.
- 12 successful local IPv4 TCP frame recoveries; 2 corrupted/oversized frame rejections.
- Exact canonical source: 214 UTF-8 bytes, dual OBS JSON frame 698,894 bytes, deflated payload 2,557 bytes. This is a highly compressible *single symbolic specimen* rather than a general network-bandwidth benchmark.
- Local measured TCP latencies are included only as diagnostic sampling, not a guarantee or proof of zero propagation delay.

## Next target

Replace thousand-digit decimal mirrored coordinate serialization on the wire with a compact, versioned byte-encoding that retains the existing exact OBS complement mathematics. Benchmark Rust/C++/Node over the **same network workload** and validate p50/p95/p99 latency, memory, resource bounds, and independent endpoint compatibility. Physical quantum entanglement needs experimentally verifiable quantum-state tests and quantum hardware; dual classical recoveries do not establish it.